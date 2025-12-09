import httpx
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Envio import (
    Envio, 
    EnvioSolicitudSchema,
    EnvioRespuestaSchema, 
    EnvioResponseSchema
)



# Configurar logger en lugar de prints
logger = logging.getLogger(__name__)

# ============================================
# 🔧 CONFIGURACIÓN
# ============================================

# ⚙️ MODO DESARROLLO (usando tu mock en Render)
# ENVIOS_API_URL = "https://e-commerce-test-mm6o.onrender.com/api/envios/mock"

# ⚙️ MODO PRODUCCIÓN - SISTEMA DE ENVÍOS REAL
ENVIOS_API_URL = "https://gestion-envios-sz3x.onrender.com/ordenes"


class EnvioServices:
    
    @staticmethod
    def _crear_registro_pendiente(db: Session, datos: EnvioSolicitudSchema) -> Envio:
        """Crea el registro inicial en BD con estado PENDIENTE"""
        
        # id_pedido se deja en NULL porque el id_orden_original del otro sistema
        # no corresponde con tu tabla de pedidos
        envio = Envio(
            id_pedido=None,  # NULL - no hay relación con tabla pedido
            id_orden_externa=datos.id_orden_externa,
            id_orden_original=datos.id_orden_original,  # "P-456" guardado aquí
            servicio_origen=datos.servicio_origen,
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        logger.info(f"Envío creado en BD: ID={envio.id_envio}")
        return envio
    
    
    @staticmethod
    def _guardar_request(envio: Envio, datos: EnvioSolicitudSchema, db: Session):
        """Guarda el request en JSON para auditoría"""
        request_dict = datos.model_dump()
        envio.request_json = json.dumps(request_dict, ensure_ascii=False, indent=2)
        db.commit()
        
        logger.info(f"Enviando a: {ENVIOS_API_URL}")
        logger.debug(f"Payload: {json.dumps(request_dict, ensure_ascii=False)}")
    
    
    @staticmethod
    def _procesar_respuesta_exitosa(envio: Envio, respuesta: dict, db: Session):
        """Procesa respuesta 200/201 del servidor"""
        try:
            envio_resp = EnvioRespuestaSchema(**respuesta)
            
            envio.codigo_seguimiento = envio_resp.codigo_seguimiento
            envio.estado_actual = envio_resp.estado_actual
            envio.ubicacion_actual = envio_resp.ubicacion_actual
            
            fecha_str = envio_resp.fecha_actualizacion
            if fecha_str.endswith('Z'):
                fecha_str = fecha_str.replace('Z', '+00:00')
            envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
            
            envio.response_json = json.dumps(respuesta, ensure_ascii=False, indent=2)
            
            logger.info(f"Envío creado: {envio.codigo_seguimiento} - {envio.estado_actual}")
            
        except ValueError as e:
            envio.estado_actual = "ERROR"
            error_msg = f"Formato de respuesta inválido: {str(e)}"
            envio.response_json = f"{error_msg}\n\nRespuesta: {json.dumps(respuesta)}"
            logger.error(error_msg)
    
    
    @staticmethod
    def _procesar_error_http(envio: Envio, response: httpx.Response, db: Session):
        """Procesa errores HTTP (404, 422, 500, etc.)"""
        envio.estado_actual = "ERROR"
        
        try:
            error_body = response.json()
        except:
            error_body = response.text
        
        error_detail = {
            "status_code": response.status_code,
            "error": error_body,
            "url": ENVIOS_API_URL
        }
        
        envio.response_json = json.dumps(error_detail, ensure_ascii=False, indent=2)
        logger.error(f"Error HTTP {response.status_code}: {error_body}")
    
    
    @staticmethod
    async def _enviar_solicitud(datos: EnvioSolicitudSchema) -> httpx.Response:
        """Envía la solicitud HTTP al servidor de envíos"""
        request_dict = datos.model_dump()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ENVIOS_API_URL,
                json=request_dict,
                headers={"Content-Type": "application/json"}
            )
        
        logger.info(f"Respuesta recibida: {response.status_code}")
        return response
    
    
    @staticmethod
    async def crear_envio(db: Session, datos: EnvioSolicitudSchema) -> EnvioResponseSchema:
        """
        📦 CREAR SOLICITUD DE ENVÍO
        
        Envía la solicitud al sistema de envíos y guarda la respuesta.
        
        Args:
            db: Sesión de base de datos
            datos: Datos completos del envío
        
        Returns:
            EnvioResponseSchema con el estado del envío
        """
        
        # Validación de productos
        if not datos.productos or len(datos.productos) == 0:
            raise HTTPException(
                status_code=400,
                detail="Debe incluir al menos un producto"
            )
        
        # Validación de duplicados
        envio_existente = db.query(Envio).filter(
            Envio.id_orden_externa == datos.id_orden_externa
        ).first()
        
        if envio_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un envío con id_orden_externa: {datos.id_orden_externa}"
            )
        
        logger.info(f"Iniciando envío: {datos.id_orden_externa}")
        
        # Crear registro pendiente
        envio = EnvioServices._crear_registro_pendiente(db, datos)
        
        try:
            # Guardar request
            EnvioServices._guardar_request(envio, datos, db)
            
            # Enviar solicitud
            response = await EnvioServices._enviar_solicitud(datos)
            
            # Procesar respuesta
            if response.status_code in [200, 201]:
                respuesta = response.json()
                EnvioServices._procesar_respuesta_exitosa(envio, respuesta, db)
            else:
                EnvioServices._procesar_error_http(envio, response, db)
            
            db.commit()
            db.refresh(envio)
            
            logger.info(f"Proceso finalizado: {envio.estado_actual}")
            return EnvioResponseSchema.model_validate(envio)
            
        except httpx.TimeoutException as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Timeout: {str(e)}"
            db.commit()
            logger.error(f"Timeout: {str(e)}")
            raise HTTPException(status_code=504, detail="Timeout: El servidor no respondió")
            
        except httpx.RequestError as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error de conexión: {str(e)}"
            db.commit()
            logger.error(f"Error de conexión: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Error de conexión: {str(e)}")
            
        except Exception as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error inesperado: {str(e)}"
            db.commit()
            logger.exception("Error inesperado")
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    

    @staticmethod
    def consultar_envio(db: Session, id_orden_externa: str) -> EnvioResponseSchema:
        """
        Consultar estado de un envío por id_orden_externa
        
        Args:
            db: Sesión de base de datos
            id_orden_externa: ID de la orden externa (string)
        
        Returns:
            EnvioResponseSchema con datos limitados del envío
        """
        envio = db.query(Envio).filter(
            Envio.id_orden_externa == id_orden_externa
        ).first()
        
        if not envio:
            raise HTTPException(
                status_code=404, 
                detail=f"Envío no encontrado con id_orden_externa: {id_orden_externa}"
            )
        
        if envio.estado_actual == "ERROR":
            logger.warning(f"Envío {id_orden_externa} en ERROR. Ver response_json para detalles.")
        
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def consultar_envio_por_pedido(db: Session, id_pedido: int) -> EnvioResponseSchema:
        """Consultar envío de un pedido específico"""
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()
        if not envio:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay envío para el pedido {id_pedido}"
            )
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def actualizar_estado_webhook(db: Session, datos: dict) -> EnvioResponseSchema:
        """
        🔔 WEBHOOK: Recibir actualizaciones del sistema de envíos
        
        El sistema de envíos llama este método cuando hay cambios.
        """
        logger.info(f"🔔 Webhook recibido: {json.dumps(datos, ensure_ascii=False, indent=2)}")
        
        id_orden_externa = datos.get("id_orden_externa")
        if not id_orden_externa:
            logger.error("❌ Webhook sin id_orden_externa")
            raise HTTPException(
                status_code=400,
                detail="Falta id_orden_externa en el webhook"
            )
        
        logger.info(f"🔍 Buscando envío con id_orden_externa: {id_orden_externa}")
        
        # Buscar el envío
        envio = db.query(Envio).filter(
            Envio.id_orden_externa == id_orden_externa
        ).first()
        
        if not envio:
            logger.error(f"❌ No se encontró envío con id_orden_externa: {id_orden_externa}")
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró envío con id_orden_externa: {id_orden_externa}"
            )
        
        logger.info(f"✅ Envío encontrado: id_envio={envio.id_envio}, id_pedido={envio.id_pedido}, estado_actual={envio.estado_actual}")
        
        # Guardar estado anterior para logging
        estado_anterior = envio.estado_actual
        
        # Actualizar datos
        nuevo_codigo_seguimiento = datos.get("codigo_seguimiento")
        nuevo_estado = datos.get("estado_actual")
        nueva_ubicacion = datos.get("ubicacion_actual")
        
        if nuevo_codigo_seguimiento:
            envio.codigo_seguimiento = nuevo_codigo_seguimiento
            logger.info(f"📦 Código de seguimiento actualizado: {nuevo_codigo_seguimiento}")
        
        if nuevo_estado:
            envio.estado_actual = nuevo_estado
            logger.info(f"📊 Estado actualizado: {estado_anterior} -> {nuevo_estado}")
        
        if nueva_ubicacion:
            envio.ubicacion_actual = nueva_ubicacion
            logger.info(f"📍 Ubicación actualizada: {nueva_ubicacion}")
        
        # Actualizar fecha
        fecha_str = datos.get("fecha_actualizacion")
        if fecha_str:
            if fecha_str.endswith('Z'):
                fecha_str = fecha_str.replace('Z', '+00:00')
            envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
        
        # Guardar historial en response_json
        try:
            actualizaciones = json.loads(envio.response_json) if envio.response_json else {}
        except:
            actualizaciones = {}
        
        if "historial_webhooks" not in actualizaciones:
            actualizaciones["historial_webhooks"] = []
        
        actualizaciones["historial_webhooks"].append({
            "fecha": datetime.utcnow().isoformat(),
            "datos": datos
        })
        
        envio.response_json = json.dumps(actualizaciones, ensure_ascii=False, indent=2)
        
        # Actualizar estado del pedido relacionado si existe
        if envio.id_pedido:
            from app.models.Pedido import Pedido
            pedido = db.query(Pedido).filter(Pedido.id_pedido == envio.id_pedido).first()
            if pedido:
                nuevo_estado_envio = datos.get("estado_actual", envio.estado_actual)
                
                # Mapear estados del envío a estados del pedido
                estado_pedido_anterior = pedido.estado
                
                if nuevo_estado_envio:
                    nuevo_estado_envio_upper = nuevo_estado_envio.upper()
                    
                    # Mapeo de estados
                    if nuevo_estado_envio_upper in ["EN_TRANSITO", "ENVIADO", "EN CAMINO", "SHIPPED"]:
                        if pedido.estado not in ["ENTREGADO", "CANCELADO"]:
                            pedido.estado = "ENVIADO"
                            logger.info(f"Pedido {pedido.id_pedido} actualizado a ENVIADO (envío: {nuevo_estado_envio})")
                    
                    elif nuevo_estado_envio_upper in ["ENTREGADO", "DELIVERED", "COMPLETADO"]:
                        pedido.estado = "ENTREGADO"
                        logger.info(f"Pedido {pedido.id_pedido} actualizado a ENTREGADO (envío: {nuevo_estado_envio})")
                    
                    elif nuevo_estado_envio_upper in ["CANCELADO", "CANCELLED", "CANCELADO"]:
                        if pedido.estado != "ENTREGADO":
                            pedido.estado = "CANCELADO"
                            logger.info(f"Pedido {pedido.id_pedido} actualizado a CANCELADO (envío: {nuevo_estado_envio})")
                    
                    elif nuevo_estado_envio_upper in ["ERROR", "FALLIDO", "FAILED"]:
                        # No cambiar el estado del pedido si hay error en el envío
                        logger.warning(f"Error en envío {envio.id_envio} pero manteniendo estado del pedido {pedido.id_pedido}")
        
        try:
            db.commit()
            db.refresh(envio)
            logger.info(f"✅ Commit exitoso - Envío {envio.id_envio} actualizado a estado: {envio.estado_actual}")
        except Exception as e:
            logger.error(f"❌ Error al hacer commit: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al guardar actualización: {str(e)}"
            )
        
        return EnvioResponseSchema.model_validate(envio)