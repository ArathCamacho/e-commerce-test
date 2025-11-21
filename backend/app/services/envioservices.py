import httpx
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Envio import (
    Envio, 
    EnvioSolicitudSchema,
    EnvioRespuestaSchema, 
    EnvioResponseSchema
)
from app.models.Pedido import Pedido  # ✅ Agregar este import

# ✅ URL CORREGIDA del sistema de envíos
ENVIOS_API_URL = "https://gestion-envios-sz3x.onrender.com/api/envios/crear"

# ⚠️ IMPORTANTE: Cambia esta URL por la tuya cuando despliegues
# Ejemplos:
# - Local: "http://localhost:8000/api/envios/webhook"
# - Render: "https://tu-app.onrender.com/api/envios/webhook"
MI_WEBHOOK_URL = "https://tu-ecommerce-api.onrender.com/api/envios/webhook"


class EnvioServices:
    
    @staticmethod
    async def crear_envio(db: Session, datos: EnvioSolicitudSchema):
        """
        📦 CREAR SOLICITUD DE ENVÍO
        
        Envía la solicitud al sistema de envíos externo y guarda la respuesta.
        
        Request que se envía:
        {
          "id_orden_externa": "ECM-2025-00002",
          "id_orden_original": 2,
          "servicio_origen": "ecommerce",
          "datos_cliente": {
            "nombre": "Juan Pérez",
            "telefono": "6621234567",
            "email": "juan@example.com",
            "direccion_completa": "Calle Sol #45",
            "ciudad": "Hermosillo",
            "estado": "Sonora",
            "codigo_postal": "83100"
          },
          "productos": [
            {
              "id_producto": 1,
              "nombre": "Playera Básica",
              "cantidad": 2,
              "precio": 199.99
            }
          ],
          "webhook_url": "https://tu-api.com/api/envios/webhook"
        }
        
        Response esperado:
        {
          "id_orden_externa": "ECM-2025-00002",
          "codigo_seguimiento": "ENV-ABC123",
          "estado_actual": "EN_PREPARACION",
          "ubicacion_actual": "Centro de distribución",
          "fecha_actualizacion": "2025-11-20T10:30:00Z"
        }
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO CREACIÓN DE ENVÍO")
        print(f"{'='*60}\n")
        
        # Validaciones básicas
        if not datos.productos or len(datos.productos) == 0:
            raise HTTPException(
                status_code=400,
                detail="❌ Debe incluir al menos un producto"
            )
        
        print(f"📦 Datos recibidos:")
        print(f"   ID orden externa: {datos.id_orden_externa}")
        print(f"   ID orden original: {datos.id_orden_original}")
        print(f"   Servicio: {datos.servicio_origen}")
        print(f"   Cliente: {datos.datos_cliente.nombre}")
        print(f"   Email: {datos.datos_cliente.email}")
        print(f"   Productos: {len(datos.productos)}")
        
        # 1. Crear registro en BD (estado PENDIENTE)
        # ✅ Validar si el pedido existe antes de asignarlo
        pedido_existe = db.query(Pedido).filter(
            Pedido.id_pedido == datos.id_orden_original
        ).first() if datos.id_orden_original else None
        
        envio = Envio(
            id_pedido=datos.id_orden_original if pedido_existe else None,
            id_orden_externa=datos.id_orden_externa,
            id_orden_original=datos.id_orden_original,
            servicio_origen=datos.servicio_origen,
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        if not pedido_existe and datos.id_orden_original:
            print(f"⚠️ ADVERTENCIA: El pedido {datos.id_orden_original} no existe en la BD")
            print(f"   El envío se creará sin referencia al pedido")
        
        print(f"\n✅ Registro de envío creado en BD: ID={envio.id_envio}")
        
        try:
            # 2. Preparar solicitud CON WEBHOOK
            request_dict = datos.model_dump()
            
            # ⭐ AGREGAR WEBHOOK_URL (requerido por el sistema de envíos)
            request_dict["webhook_url"] = MI_WEBHOOK_URL
            
            # Guardar request para auditoría
            envio.request_json = json.dumps(request_dict, ensure_ascii=False, indent=2)
            db.commit()
            
            print(f"\n📤 ENVIANDO A API EXTERNA:")
            print(f"   URL: {ENVIOS_API_URL}")
            print(f"   Webhook: {MI_WEBHOOK_URL}")
            print(f"\n   Payload completo:")
            print(json.dumps(request_dict, ensure_ascii=False, indent=2))
            
            # 3. Enviar a API externa con timeout de 30 segundos
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    ENVIOS_API_URL,
                    json=request_dict,
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"\n📥 RESPUESTA DE API EXTERNA:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"\n   Body completo:")
            print(response.text)
            
            # 4. Procesar respuesta según status code
            if response.status_code in [200, 201]:
                respuesta = response.json()
                
                try:
                    # Validar que la respuesta tenga el formato correcto
                    envio_resp = EnvioRespuestaSchema(**respuesta)
                    
                    # Actualizar envío con datos recibidos
                    envio.codigo_seguimiento = envio_resp.codigo_seguimiento
                    envio.estado_actual = envio_resp.estado_actual
                    envio.ubicacion_actual = envio_resp.ubicacion_actual
                    
                    # Parsear fecha ISO 8601
                    fecha_str = envio_resp.fecha_actualizacion
                    if fecha_str.endswith('Z'):
                        fecha_str = fecha_str.replace('Z', '+00:00')
                    envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
                    
                    # Guardar respuesta completa para auditoría
                    envio.response_json = json.dumps(respuesta, ensure_ascii=False, indent=2)
                    
                    print(f"\n✅ ENVÍO CREADO EXITOSAMENTE:")
                    print(f"   ID Envío: {envio.id_envio}")
                    print(f"   Código seguimiento: {envio.codigo_seguimiento}")
                    print(f"   Estado: {envio.estado_actual}")
                    print(f"   Ubicación: {envio.ubicacion_actual}")
                    print(f"   Última actualización: {envio.fecha_actualizacion}")
                    
                except ValueError as e:
                    # Respuesta exitosa pero con formato inválido
                    envio.estado_actual = "ERROR"
                    error_msg = f"❌ Formato de respuesta inválido\n"
                    error_msg += f"Campos esperados: id_orden_externa, codigo_seguimiento, "
                    error_msg += f"estado_actual, ubicacion_actual, fecha_actualizacion\n"
                    error_msg += f"Error: {str(e)}"
                    envio.response_json = f"{error_msg}\n\nRespuesta recibida:\n{response.text}"
                    
                    print(f"\n❌ ERROR EN FORMATO DE RESPUESTA:")
                    print(f"   {error_msg}")
                    
            else:
                # Error HTTP (404, 422, 500, etc.)
                envio.estado_actual = "ERROR"
                
                try:
                    error_body = response.json()
                    error_detail = {
                        "status_code": response.status_code,
                        "error": error_body,
                        "url": ENVIOS_API_URL
                    }
                except:
                    error_detail = {
                        "status_code": response.status_code,
                        "error": response.text,
                        "url": ENVIOS_API_URL
                    }
                
                envio.response_json = json.dumps(error_detail, ensure_ascii=False, indent=2)
                
                print(f"\n❌ ERROR HTTP {response.status_code}")
                print(f"   URL: {ENVIOS_API_URL}")
                print(f"   Respuesta: {response.text}")
                
                # Mensajes específicos según el error
                if response.status_code == 404:
                    print(f"\n⚠️ ERROR 404 - ENDPOINT NO ENCONTRADO")
                    print(f"   Posibles causas:")
                    print(f"   1. La URL no existe o cambió")
                    print(f"   2. El servidor está caído")
                    print(f"   3. La ruta es incorrecta")
                    print(f"\n   URL actual: {ENVIOS_API_URL}")
                    print(f"   Verifica con el equipo de envíos que esta sea la URL correcta")
                    
                elif response.status_code == 422:
                    print(f"\n⚠️ ERROR 422 - DATOS INVÁLIDOS")
                    print(f"   El servidor rechazó los datos enviados")
                    print(f"   Verifica que los campos coincidan con su esquema")
                    print(f"   Revisa el 'error' en response_json para más detalles")
                    
                elif response.status_code >= 500:
                    print(f"\n⚠️ ERROR {response.status_code} - FALLO DEL SERVIDOR")
                    print(f"   El servidor de envíos tiene un error interno")
                    print(f"   No es un problema de tu código")
            
            # Guardar cambios
            db.commit()
            db.refresh(envio)
            
            print(f"\n{'='*60}")
            print(f"🏁 PROCESO FINALIZADO - Envío ID: {envio.id_envio}")
            print(f"   Estado final: {envio.estado_actual}")
            print(f"{'='*60}\n")
            
            return EnvioResponseSchema.model_validate(envio)
            
        except httpx.TimeoutException as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"⏱️ Timeout: El servidor no respondió en 30 segundos.\n{str(e)}"
            db.commit()
            
            print(f"\n❌ TIMEOUT: La API externa no respondió en 30 segundos")
            print(f"   Posibles causas:")
            print(f"   1. El servidor está sobrecargado")
            print(f"   2. Problemas de red")
            print(f"   3. El servidor está reiniciando (Render free tier)")
            
            raise HTTPException(
                status_code=504, 
                detail="Timeout: La API de envíos no respondió en 30 segundos"
            )
            
        except httpx.RequestError as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"🔌 Error de conexión: {str(e)}"
            db.commit()
            
            print(f"\n❌ ERROR DE CONEXIÓN:")
            print(f"   {str(e)}")
            print(f"   Verifica:")
            print(f"   1. Que tengas conexión a internet")
            print(f"   2. Que la URL sea correcta: {ENVIOS_API_URL}")
            print(f"   3. Que el servidor esté activo")
            
            raise HTTPException(
                status_code=503, 
                detail=f"Error de conexión: {str(e)}"
            )
            
        except Exception as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"💥 Error inesperado: {str(e)}"
            db.commit()
            
            print(f"\n❌ ERROR INESPERADO: {str(e)}")
            import traceback
            traceback.print_exc()
            
            raise HTTPException(
                status_code=500, 
                detail=f"Error interno: {str(e)}"
            )
    
    
    @staticmethod
    def consultar_envio(db: Session, id_envio: int):
        """🔍 Consultar estado de un envío por ID"""
        envio = db.query(Envio).filter(Envio.id_envio == id_envio).first()
        if not envio:
            raise HTTPException(status_code=404, detail="Envío no encontrado")
        
        # Si hay error, mostrar detalles en consola
        if envio.estado_actual == "ERROR":
            print(f"\n⚠️ ENVÍO {id_envio} EN ERROR:")
            print(f"\n📤 Request enviado:")
            print(envio.request_json)
            print(f"\n📥 Response recibido:")
            print(envio.response_json)
        
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def consultar_envio_por_pedido(db: Session, id_pedido: int):
        """🔍 Consultar envío de un pedido específico"""
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()
        if not envio:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay envío para el pedido {id_pedido}"
            )
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def actualizar_estado_webhook(db: Session, datos: dict):
        """
        🔔 WEBHOOK: Recibir actualizaciones del sistema de envíos
        
        El sistema de envíos llamará este método cuando haya cambios.
        
        Datos esperados:
        {
            "id_orden_externa": "ECM-2025-00002",
            "codigo_seguimiento": "ENV-ABC123",
            "estado_actual": "EN_TRANSITO",
            "ubicacion_actual": "Centro de distribución Guadalajara",
            "fecha_actualizacion": "2025-11-20T15:30:00Z"
        }
        """
        print(f"\n{'='*60}")
        print(f"🔔 WEBHOOK RECIBIDO - Actualización de envío")
        print(f"{'='*60}\n")
        print(json.dumps(datos, ensure_ascii=False, indent=2))
        
        id_orden_externa = datos.get("id_orden_externa")
        if not id_orden_externa:
            raise HTTPException(
                status_code=400,
                detail="Falta id_orden_externa en el webhook"
            )
        
        # Buscar el envío por id_orden_externa
        envio = db.query(Envio).filter(
            Envio.id_orden_externa == id_orden_externa
        ).first()
        
        if not envio:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró envío con id_orden_externa: {id_orden_externa}"
            )
        
        # Actualizar datos
        envio.codigo_seguimiento = datos.get("codigo_seguimiento", envio.codigo_seguimiento)
        envio.estado_actual = datos.get("estado_actual", envio.estado_actual)
        envio.ubicacion_actual = datos.get("ubicacion_actual", envio.ubicacion_actual)
        
        # Actualizar fecha
        fecha_str = datos.get("fecha_actualizacion")
        if fecha_str:
            if fecha_str.endswith('Z'):
                fecha_str = fecha_str.replace('Z', '+00:00')
            envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
        
        # Guardar actualización en response_json (historial)
        try:
            actualizaciones = json.loads(envio.response_json) if envio.response_json else {}
        except:
            actualizaciones = {}
        
        # Agregar timestamp de la actualización
        if "historial_webhooks" not in actualizaciones:
            actualizaciones["historial_webhooks"] = []
        
        actualizaciones["historial_webhooks"].append({
            "fecha": datetime.utcnow().isoformat(),
            "datos": datos
        })
        
        envio.response_json = json.dumps(actualizaciones, ensure_ascii=False, indent=2)
        
        db.commit()
        db.refresh(envio)
        
        print(f"\n✅ ENVÍO ACTUALIZADO VÍA WEBHOOK:")
        print(f"   ID: {envio.id_envio}")
        print(f"   Estado: {envio.estado_actual}")
        print(f"   Ubicación: {envio.ubicacion_actual}")
        print(f"   Fecha: {envio.fecha_actualizacion}")
        print(f"{'='*60}\n")
        
        return EnvioResponseSchema.model_validate(envio)