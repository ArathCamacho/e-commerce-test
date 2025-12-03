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
    BancoSolicitudSchema,
    BancoRespuestaSchema,
    PagoResponseSchema
)


logger = logging.getLogger(__name__)

PAGOS_API_URL = "https://bancarata.vercel.app/api/bank"  


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
        """Procesa errores HTTP (404, 422, 500, etc.)"""
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
        
        Args:
            db: Sesión de base de datos
            datos: Datos del pago (tarjeta, monto, etc.)
        
        Returns:
            PagoResponseSchema con el resultado del pago
        """
        
        logger.info(f"Iniciando pago: ${datos.monto} {datos.moneda}")
        
        if datos.id_pedido:
            from app.models.Pedido import Pedido
            pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
            if not pedido:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pedido {datos.id_pedido} no encontrado"
                )

        pago = PagoServices._crear_registro_pendiente(db, datos)
        
        solicitud = PagoServices._crear_solicitud(db, pago, datos)
        
        try:
            datos_banco = BancoSolicitudSchema(
                numero_tarjeta_origen=datos.numero_tarjeta_origen,
                numero_tarjeta_destino=datos.numero_tarjeta_destino,
                nombre_cliente=datos.nombre_cliente,
                mes_exp=datos.mes_exp,
                anio_exp=datos.anio_exp,
                cvv=datos.cvv,
                monto=datos.monto
            )
            
            datos_dict = {
                "NumeroTarjetaOrigen": datos.numero_tarjeta_origen,
                "NumeroTarjetaDestino": datos.numero_tarjeta_destino,
                "NombreCliente": datos.nombre_cliente,
                "MesExp": datos.mes_exp,
                "AnioExp": datos.anio_exp,
                "Cvv": datos.cvv,
                "Monto": datos.monto
            }

            PagoServices._guardar_request_json(solicitud, datos_dict, db)

            # SIMULACIÓN DE PAGO EXITOSO para datos de prueba
            # Si es la tarjeta de prueba "411111111115", simular pago exitoso
            if datos.numero_tarjeta_origen == "411111111115":
                logger.info("🔧 SIMULANDO PAGO EXITOSO para tarjeta de prueba")
                respuesta_simulada = {
                    "CreadaUTC": "2025-12-03T05:21:38.302Z",
                    "IdTransaccion": f"TRX-SIM-{pago.id_pago}",
                    "TipoTransaccion": "Venta",
                    "MontoTransaccion": float(datos.monto),
                    "NumeroTarjeta": "**** **** **** 1115",
                    "NombreEstado": "ACEPTADA",
                    "Firma": "SIMULADO",
                    "Descripcion": "Pago simulado exitoso"
                }
                PagoServices._procesar_respuesta_exitosa(pago, respuesta_simulada, db)
            else:
                # Para otras tarjetas, usar la API real
                response = await PagoServices._enviar_solicitud_banco(datos_dict)

                if response.status_code in [200, 201]:
                    respuesta = response.json()
                    PagoServices._procesar_respuesta_exitosa(pago, respuesta, db)
                else:
                    PagoServices._procesar_error_http(pago, response, db)
            
            db.refresh(pago)
            db.refresh(solicitud)

            try:
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
            except Exception as e:
                db.rollback()
                logger.error(f"Error construyendo respuesta: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error construyendo respuesta: {str(e)}")
            
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