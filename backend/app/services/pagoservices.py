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

# Configurar logger
logger = logging.getLogger(__name__)

# ============================================
# 🔧 CONFIGURACIÓN
# ============================================

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
        
        logger.info(f"✅ Pago creado en BD: ID={pago.id_pago}")
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
        
        logger.info(f"📤 Solicitud creada: ID={solicitud.id_solicitud}")
        return solicitud
    
    
    @staticmethod
    def _guardar_request_json(solicitud: PagoSolicitud, datos: BancoSolicitudSchema, db: Session):
        """Guarda el JSON completo de la solicitud para auditoría"""
        request_dict = datos.model_dump()
        solicitud.request_json = json.dumps(request_dict, ensure_ascii=False, indent=2)
        db.commit()
        
        logger.info(f"🌐 Enviando a: {PAGOS_API_URL}")
        logger.debug(f"📦 Payload: {json.dumps(request_dict, ensure_ascii=False)}")
    
    
    @staticmethod
    def _procesar_respuesta_exitosa(pago: Pago, respuesta: dict, db: Session):
        """Procesa respuesta 200/201 del banco y crea PagoRespuesta"""
        try:
            banco_resp = BancoRespuestaSchema(**respuesta)
            
            # Crear registro de respuesta
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                id_transaccion=banco_resp.id_transaccion,
                tipo_transaccion=banco_resp.tipo,
                monto_transaccion=banco_resp.monto,
                numero_tarjeta=banco_resp.numero_tarjeta,
                nombre_estado=banco_resp.id_estado_transaccion,
                firma=banco_resp.firma,
                mensaje=banco_resp.mensaje,
                response_json=json.dumps(respuesta, ensure_ascii=False, indent=2)
            )
            
            # Parsear fecha
            fecha_str = banco_resp.creada_utc
            if fecha_str.endswith('Z'):
                fecha_str = fecha_str.replace('Z', '+00:00')
            pago_respuesta.creada_utc = datetime.fromisoformat(fecha_str)
            
            db.add(pago_respuesta)
            
            # Actualizar estado del pago según respuesta del banco
            estado_banco = banco_resp.id_estado_transaccion.upper()
            if estado_banco in ["APROBADO", "APPROVED", "SUCCESS", "EXITOSO"]:
                pago.estado = "APROBADO"
            elif estado_banco in ["RECHAZADO", "REJECTED", "DECLINED", "DENEGADO"]:
                pago.estado = "RECHAZADO"
            else:
                pago.estado = estado_banco
            
            db.commit()
            
            logger.info(f"✅ Pago procesado: {pago.id_pago} - {pago.estado}")
            
        except ValueError as e:
            pago.estado = "ERROR"
            error_msg = f"Formato de respuesta inválido: {str(e)}"
            
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=error_msg,
                response_json=f"{error_msg}\n\nRespuesta: {json.dumps(respuesta)}"
            )
            db.add(pago_respuesta)
            db.commit()
            
            logger.error(f"❌ {error_msg}")
    
    
    @staticmethod
    def _procesar_error_http(pago: Pago, response: httpx.Response, db: Session):
        """Procesa errores HTTP (404, 422, 500, etc.)"""
        pago.estado = "ERROR"
        
        try:
            error_body = response.json()
        except:
            error_body = response.text
        
        error_detail = {
            "status_code": response.status_code,
            "error": error_body,
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
        
        logger.error(f"❌ Error HTTP {response.status_code}: {error_body}")
    
    
    @staticmethod
    async def _enviar_solicitud_banco(datos: BancoSolicitudSchema) -> httpx.Response:
        """Envía la solicitud HTTP al banco"""
        request_dict = datos.model_dump()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PAGOS_API_URL,
                json=request_dict,
                headers={"Content-Type": "application/json"}
            )
        
        logger.info(f"📥 Respuesta del banco: {response.status_code}")
        return response
    
    
    @staticmethod
    async def procesar_pago(db: Session, datos: PagoIniciarSchema) -> PagoResponseSchema:
        """
        💳 PROCESAR PAGO CON EL BANCO
        
        Flujo completo:
        1. Crea registro de pago (PENDIENTE)
        2. Crea solicitud con datos enviados
        3. Envía POST al banco
        4. Crea respuesta con lo que el banco regresa
        5. Actualiza estado del pago
        
        Args:
            db: Sesión de base de datos
            datos: Datos del pago (tarjeta, monto, etc.)
        
        Returns:
            PagoResponseSchema con el resultado del pago
        """
        
        logger.info(f"💳 Iniciando pago: ${datos.monto} {datos.moneda}")
        
        # Validar pedido si viene
        if datos.id_pedido:
            from app.models.Pedido import Pedido
            pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
            if not pedido:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pedido {datos.id_pedido} no encontrado"
                )
        
        # PASO 1: Crear registro de pago
        pago = PagoServices._crear_registro_pendiente(db, datos)
        
        # PASO 2: Crear solicitud
        solicitud = PagoServices._crear_solicitud(db, pago, datos)
        
        try:
            # PASO 3: Preparar datos para el banco
            datos_banco = BancoSolicitudSchema(
                id_tarjeta_origen=datos.numero_tarjeta_origen,
                id_tarjeta_destino=datos.numero_tarjeta_destino,
                nombre=datos.nombre_cliente,
                mes_exp=datos.mes_exp,
                anio_exp=datos.anio_exp,
                cvv=datos.cvv,
                monto=datos.monto,
                moneda=datos.moneda,
                tipo=datos.tipo
            )
            
            # Guardar request JSON
            PagoServices._guardar_request_json(solicitud, datos_banco, db)
            
            # PASO 4: Enviar al banco
            response = await PagoServices._enviar_solicitud_banco(datos_banco)
            
            # PASO 5: Procesar respuesta
            if response.status_code in [200, 201]:
                respuesta = response.json()
                PagoServices._procesar_respuesta_exitosa(pago, respuesta, db)
            else:
                PagoServices._procesar_error_http(pago, response, db)
            
            db.refresh(pago)
            db.refresh(solicitud)
            
            # Construir respuesta completa
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
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Timeout: {str(e)}"
            )
            db.add(pago_respuesta)
            db.commit()
            logger.error(f"⏱️ Timeout: {str(e)}")
            raise HTTPException(status_code=504, detail="Timeout: El banco no respondió")
            
        except httpx.RequestError as e:
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Error de conexión: {str(e)}"
            )
            db.add(pago_respuesta)
            db.commit()
            logger.error(f"🔌 Error de conexión: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")
            
        except Exception as e:
            pago.estado = "ERROR"
            pago_respuesta = PagoRespuesta(
                id_pago=pago.id_pago,
                nombre_estado="ERROR",
                mensaje=f"Error inesperado: {str(e)}"
            )
            db.add(pago_respuesta)
            db.commit()
            logger.exception("💥 Error inesperado")
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