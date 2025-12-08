import httpx
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Pago import (
    Pago,
    PagoSolicitud,
    PagoRespuesta,
    PagoIniciarSchema,
    PagoFrontendSchema,
    BancoSolicitudSchema,
    BancoRespuestaSchema,
    PagoResponseSchema
)


logger = logging.getLogger(__name__)

PAGOS_API_URL = "https://bancarata.vercel.app/api/bank"
MI_TARJETA_DESTINO = "4111111111111115"


class PagoServices:
    
    @staticmethod
    def _crear_registro_pendiente(db: Session, datos: PagoIniciarSchema) -> Pago:
        """Crea el registro inicial del pago con estado PENDIENTE"""
        
        pago = Pago(
            id_pedido=datos.id_pedido,
            monto=datos.monto,
            moneda=datos.moneda,
            estado="PENDIENTE",
            metodo="tarjeta"
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        
        logger.info(f"Pago creado en BD: ID={pago.id_pago}")
        return pago
    
    
    @staticmethod
    def _crear_solicitud(db: Session, pago: Pago, datos: PagoIniciarSchema) -> PagoSolicitud:
        """Crea el registro de solicitud con los datos enviados al banco"""
        
        solicitud = PagoSolicitud(
            id_pago=pago.id_pago,
            numero_tarjeta_origen=datos.numero_tarjeta_origen,
            numero_tarjeta_destino=datos.numero_tarjeta_destino,
            nombre_cliente=datos.nombre_cliente,
            mes_exp=datos.mes_exp,
            anio_exp=datos.anio_exp,
            cvv=datos.cvv,
            monto=datos.monto,
            moneda=datos.moneda,
            tipo=datos.tipo
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        
        logger.info(f"Solicitud creada: ID={solicitud.id_solicitud}")
        return solicitud
    
    
    @staticmethod
    def _guardar_request_json(solicitud: PagoSolicitud, datos_dict: dict, db: Session):
        """Guarda el JSON completo de la solicitud para auditoría"""
        solicitud.request_json = json.dumps(datos_dict, ensure_ascii=False, indent=2)
        db.commit()
        
        logger.info(f"Enviando a: {PAGOS_API_URL}")
        logger.debug(f"Payload: {json.dumps(datos_dict, ensure_ascii=False)}")
    
    
    @staticmethod
    async def _crear_envio_automatico(db: Session, pago: Pago):
        """
        📦 CREAR ENVÍO AUTOMÁTICAMENTE DESPUÉS DE PAGO APROBADO
        
        Args:
            db: Sesión de base de datos
            pago: Objeto Pago ya aprobado
        """
        try:
            from app.models.Pedido import Pedido
            from app.models.Cliente import Cliente
            from app.models.Direccion import Direccion
            from app.models.Envio import EnvioSolicitudSchema, DatosClienteEnvioSchema, ProductoEnvioSchema
            from app.services.envioservices import EnvioServices
            
            # Obtener el pedido completo
            pedido = db.query(Pedido).filter(Pedido.id_pedido == pago.id_pedido).first()
            if not pedido:
                logger.error(f"No se encontró pedido {pago.id_pedido} para crear envío")
                return
            
            # Obtener datos del cliente
            cliente = db.query(Cliente).filter(Cliente.id_cliente == pedido.id_cliente).first()
            if not cliente:
                logger.error(f"No se encontró cliente {pedido.id_cliente}")
                return
            
            # Obtener dirección
            direccion = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
            if not direccion:
                logger.error(f"No se encontró dirección {pedido.id_direccion}")
                return
            
            # Construir dirección completa
            direccion_completa = f"{direccion.calle}, {direccion.ciudad}, {direccion.estado}, CP {direccion.codigo_postal}"

            # Construir lista de productos usando consulta SQL directa
            from sqlalchemy import text
            productos_query = text("""
                SELECT
                    pi.id_producto, pi.cantidad, pi.precio_unitario,
                    p.nombre as nombre_producto
                FROM pedido_item pi
                JOIN producto p ON pi.id_producto = p.id_producto
                WHERE pi.id_pedido = :id_pedido
            """)

            productos_result = db.execute(productos_query, {"id_pedido": pedido.id_pedido}).fetchall()

            productos_envio = []
            for item in productos_result:
                productos_envio.append(ProductoEnvioSchema(
                    sku=f"PROD-{item.id_producto}",
                    nombre=item.nombre_producto,
                    cantidad=item.cantidad,
                    precio_unitario=float(item.precio_unitario)
                ))
            
            # Crear solicitud de envío
            envio_solicitud = EnvioSolicitudSchema(
                id_orden_externa=f"PEDIDO-{pedido.id_pedido}",
                id_orden_original=f"P-{pedido.id_pedido}",
                servicio_origen="ecommerce",
                webhook_url="https://e-commerce-test-mm6o.onrender.com/api/envios/webhook",
                datos_cliente=DatosClienteEnvioSchema(
                    nombre=f"{cliente.nombre} {cliente.apellido}",
                    telefono=cliente.telefono or "0000000000",
                    email=cliente.correo,
                    direccion=direccion_completa
                ),
                productos=productos_envio
            )
            
            logger.info(f"🚚 Creando envío automático para pedido {pedido.id_pedido}")
            
            # Llamar al servicio de envíos
            envio_response = await EnvioServices.crear_envio(db, envio_solicitud)
            
            # Actualizar el envío con el id_pedido correcto
            from app.models.Envio import Envio
            envio = db.query(Envio).filter(Envio.id_envio == envio_response.id_envio).first()
            if envio:
                envio.id_pedido = pedido.id_pedido
                db.commit()
                logger.info(f"✅ Envío {envio.id_envio} creado y vinculado a pedido {pedido.id_pedido}")
            
        except Exception as e:
            logger.error(f"❌ Error al crear envío automático: {str(e)}")
            logger.exception("Detalles del error:")
            # No lanzamos excepción para que el pago se complete aunque falle el envío
    
    
    @staticmethod
    def _procesar_respuesta_exitosa(pago: Pago, respuesta: dict, db: Session):
        """Procesa respuesta 200/201 del banco y crea PagoRespuesta"""
        try:
            banco_resp = BancoRespuestaSchema(**respuesta)

            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                id_transaccion=banco_resp.IdTransaccion, 
                tipo_transaccion=banco_resp.TipoTransaccion,
                monto_transaccion=banco_resp.MontoTransaccion,
                numero_tarjeta=banco_resp.NumeroTarjeta,
                nombre_estado=banco_resp.NombreEstado,
                firma=banco_resp.Firma,
                mensaje=banco_resp.Mensaje,
                response_json=json.dumps(respuesta, ensure_ascii=False, indent=2)
            )
            fecha_str = banco_resp.CreadaUTC
            if fecha_str.endswith('Z'):
                fecha_str = fecha_str.replace('Z', '+00:00')
            pago_respuesta.creada_utc = datetime.fromisoformat(fecha_str)
            
            db.add(pago_respuesta)

            estado_banco = banco_resp.NombreEstado.upper()

            if estado_banco in ["ACEPTADA", "COMPLETADA", "APROBADA", "APPROVED", "SUCCESS", "EXITOSO"]:
                pago.estado = "APROBADO"

                # Actualizar estado del pedido si existe
                if pago.id_pedido:
                    from app.models.Pedido import Pedido
                    pedido = db.query(Pedido).filter(Pedido.id_pedido == pago.id_pedido).first()
                    if pedido:
                        pedido.estado = "PAGADO"
                        logger.info(f"Pedido {pedido.id_pedido} actualizado a PAGADO")

            elif estado_banco in ["RECHAZADA", "RECHAZADO", "REJECTED", "DECLINED", "DENEGADO"]:
                pago.estado = "RECHAZADO"
            else:
                pago.estado = estado_banco
            
            db.commit()
            
            logger.info(f"Pago procesado: {pago.id_pago} - {pago.estado}")
            logger.info(f"Transacción: {banco_resp.IdTransaccion}")
            
        except ValueError as e:
            pago.estado = "ERROR"
            error_msg = f"Error de validación: {str(e)[:100]}"
            
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=error_msg, 
                response_json=json.dumps({
                    "error": str(e),
                    "respuesta_banco": respuesta
                }, ensure_ascii=False, indent=2)
            )
            db.add(pago_respuesta)
            db.commit()
            
            logger.error(f"{error_msg}")
    
    
    @staticmethod
    def _procesar_error_http(pago: Pago, response: httpx.Response, db: Session):
        """
        Procesa errores HTTP (404, 422, 500, etc.)
        IMPORTANTE: Si es un 400 con JSON válido del banco, lo procesamos como respuesta válida
        """
        try:
            # Intentar parsear como respuesta del banco
            respuesta_json = response.json()
            
            # Si tiene la estructura de respuesta del banco, procesarla
            if 'IdTransaccion' in respuesta_json and 'NombreEstado' in respuesta_json:
                logger.warning(f"Banco respondió con {response.status_code} pero tiene estructura válida. Procesando...")
                PagoServices._procesar_respuesta_exitosa(pago, respuesta_json, db)
                return
        except:
            pass  # No es JSON válido del banco, continuar con error
        
        # Si llegamos aquí, es un error real
        pago.estado = "ERROR"
        
        try:
            error_body = response.json()
        except:
            error_body = response.text[:200]  
        
        error_detail = {
            "status_code": response.status_code,
            "error": str(error_body)[:200],  
            "url": PAGOS_API_URL
        }
        
        pago_respuesta = PagoRespuesta(
            id_pago=pago.id_pago,
            nombre_estado="ERROR",
            mensaje=f"Error HTTP {response.status_code}", 
            response_json=json.dumps(error_detail, ensure_ascii=False, indent=2)
        )
        
        db.add(pago_respuesta)
        db.commit()
        
        logger.error(f"Error HTTP {response.status_code}: {error_body}")
    
    
    @staticmethod
    async def _enviar_solicitud_banco(datos_dict: dict) -> httpx.Response:
        """Envía la solicitud HTTP al banco"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PAGOS_API_URL,
                json=datos_dict,
                headers={"Content-Type": "application/json"}
            )
        
        logger.info(f"Respuesta del banco: {response.status_code}")
        return response
    
    
    @staticmethod
    async def procesar_pago_frontend(db: Session, datos: PagoFrontendSchema) -> PagoResponseSchema:
        """
        💳 PROCESAR PAGO DESDE EL FRONTEND
        Este método recibe los datos del cliente SIN la tarjeta destino
        y automáticamente usa tu tarjeta hardcodeada
        
        Args:
            db: Sesión de base de datos
            datos: Datos del pago del cliente (sin tarjeta destino)
        
        Returns:
            PagoResponseSchema con el resultado del pago
        """
        # Convertir a PagoIniciarSchema agregando tu tarjeta destino
        datos_completos = PagoIniciarSchema(
            numero_tarjeta_origen=datos.numero_tarjeta_origen,
            numero_tarjeta_destino=MI_TARJETA_DESTINO,  # ← Hardcodeado
            nombre_cliente=datos.nombre_cliente,
            mes_exp=datos.mes_exp,
            anio_exp=datos.anio_exp,
            cvv=datos.cvv,
            monto=datos.monto,
            moneda=datos.moneda,
            tipo=datos.tipo,
            id_pedido=datos.id_pedido
        )
        
        return await PagoServices.procesar_pago(db, datos_completos)
    
    
    @staticmethod
    async def procesar_pago(db: Session, datos: PagoIniciarSchema) -> PagoResponseSchema:
        """
        💳 PROCESAR PAGO CON EL BANCO
        
        Flujo completo:
        1. Crea registro de pago (PENDIENTE)
        2. Crea solicitud con datos enviados
        3. Convierte a formato PascalCase para el banco
        4. Envía POST al banco
        5. Crea respuesta con lo que el banco regresa
        6. Actualiza estado del pago
        7. ✨ SI EL PAGO ES APROBADO → Crea envío automáticamente
        
        Args:
            db: Sesión de base de datos
            datos: Datos del pago (tarjeta, monto, etc.)
        
        Returns:
            PagoResponseSchema con el resultado del pago
        """
        
        logger.info(f"Iniciando pago: ${datos.monto} {datos.moneda}")
        
        # Validar pedido si existe
        if datos.id_pedido:
            from app.models.Pedido import Pedido
            pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
            if not pedido:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pedido {datos.id_pedido} no encontrado"
                )

        # 1. Crear registro de pago
        pago = PagoServices._crear_registro_pendiente(db, datos)
        
        # 2. Crear solicitud
        solicitud = PagoServices._crear_solicitud(db, pago, datos)
        
        try:
            # 3. Preparar datos en formato PascalCase para el banco
            datos_dict = {
                "NumeroTarjetaOrigen": datos.numero_tarjeta_origen,
                "NumeroTarjetaDestino": datos.numero_tarjeta_destino,
                "NombreCliente": datos.nombre_cliente,
                "MesExp": datos.mes_exp,
                "AnioExp": datos.anio_exp,
                "Cvv": datos.cvv,
                "Monto": datos.monto
            }
            
            # 4. Guardar request para auditoría
            PagoServices._guardar_request_json(solicitud, datos_dict, db)
            
            # 5. Enviar al banco
            response = await PagoServices._enviar_solicitud_banco(datos_dict)
            
            # 6. Procesar respuesta
            if response.status_code in [200, 201]:
                respuesta_json = response.json()
                PagoServices._procesar_respuesta_exitosa(pago, respuesta_json, db)
            else:
                # Puede ser un 400 con respuesta válida del banco o un error real
                PagoServices._procesar_error_http(pago, response, db)
            
            # 7. Refrescar para obtener los datos actualizados
            db.refresh(pago)
            
            # 🚚 ✨ NUEVO: Si el pago fue aprobado, crear envío automáticamente
            if pago.estado == "APROBADO" and pago.id_pedido:
                logger.info(f"💳 Pago aprobado, iniciando creación de envío para pedido {pago.id_pedido}")
                await PagoServices._crear_envio_automatico(db, pago)
            
            # 8. Construir respuesta
            return PagoResponseSchema(
                id_pago=pago.id_pago,
                id_pedido=pago.id_pedido,
                monto=pago.monto,
                moneda=pago.moneda,
                estado=pago.estado,
                metodo=pago.metodo,
                fecha=pago.fecha,
                numero_tarjeta_origen=solicitud.numero_tarjeta_origen,
                nombre_cliente=solicitud.nombre_cliente,
                id_transaccion=pago.respuesta.id_transaccion if pago.respuesta else None,
                nombre_estado=pago.respuesta.nombre_estado if pago.respuesta else None,
                mensaje=pago.respuesta.mensaje if pago.respuesta else None
            )
            
        except httpx.TimeoutException as e:
            db.rollback()  
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Timeout"[:200]  
            )
            db.add(pago_respuesta)
            db.commit()
            db.refresh(pago)  
            logger.error(f"⏱Timeout: {str(e)}")
            raise HTTPException(status_code=504, detail="Timeout: El banco no respondió")
            
        except httpx.RequestError as e:
            db.rollback()  
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Error de conexión"[:200]  
            )
            db.add(pago_respuesta)
            db.commit()
            db.refresh(pago)  
            logger.error(f"Error de conexión: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")
            
        except Exception as e:
            db.rollback()  
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Error inesperado"[:200]  
            )
            db.add(pago_respuesta)
            db.commit()
            db.refresh(pago)  
            logger.exception("Error inesperado")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    
    @staticmethod
    def consultar_pago(db: Session, id_pago: int) -> PagoResponseSchema:
        """Consultar estado de un pago por ID"""
        pago = db.query(Pago).filter(Pago.id_pago == id_pago).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        return PagoResponseSchema(
            id_pago=pago.id_pago,
            id_pedido=pago.id_pedido,
            monto=pago.monto,
            moneda=pago.moneda,
            estado=pago.estado,
            metodo=pago.metodo,
            fecha=pago.fecha,
            numero_tarjeta_origen=pago.solicitud.numero_tarjeta_origen if pago.solicitud else None,
            nombre_cliente=pago.solicitud.nombre_cliente if pago.solicitud else None,
            id_transaccion=pago.respuesta.id_transaccion if pago.respuesta else None,
            nombre_estado=pago.respuesta.nombre_estado if pago.respuesta else None,
            mensaje=pago.respuesta.mensaje if pago.respuesta else None
        )
    
    
    @staticmethod
    def consultar_pagos_por_pedido(db: Session, id_pedido: int):
        """Consultar todos los pagos de un pedido"""
        pagos = db.query(Pago).filter(Pago.id_pedido == id_pedido).all()
        
        if not pagos:
            raise HTTPException(
                status_code=404,
                detail=f"No hay pagos para el pedido {id_pedido}"
            )
        
        return [
            PagoResponseSchema(
                id_pago=p.id_pago,
                id_pedido=p.id_pedido,
                monto=p.monto,
                moneda=p.moneda,
                estado=p.estado,
                metodo=p.metodo,
                fecha=p.fecha,
                numero_tarjeta_origen=p.solicitud.numero_tarjeta_origen if p.solicitud else None,
                nombre_cliente=p.solicitud.nombre_cliente if p.solicitud else None,
                id_transaccion=p.respuesta.id_transaccion if p.respuesta else None,
                nombre_estado=p.respuesta.nombre_estado if p.respuesta else None,
                mensaje=p.respuesta.mensaje if p.respuesta else None
            )
            for p in pagos
        ]