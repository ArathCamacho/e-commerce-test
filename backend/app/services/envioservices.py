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

ENVIOS_API_URL = "https://api-envios-equipo.onrender.com/api/envios/crear"


class EnvioServices:
    
    @staticmethod
    async def crear_envio(db: Session, datos: EnvioSolicitudSchema):
        """
        📦 CREAR SOLICITUD DE ENVÍO (RECIBE DATOS COMPLETOS)
        
        Flujo simplificado:
        1. Recibe todos los datos ya preparados
        2. Valida estructura
        3. Envía a API externa
        4. Guarda respuesta
        
        Request esperado:
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
          ]
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
        envio = Envio(
            id_pedido=datos.id_orden_original,
            id_orden_externa=datos.id_orden_externa,
            id_orden_original=datos.id_orden_original,
            servicio_origen=datos.servicio_origen,
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        print(f"\n✅ Registro de envío creado en BD: ID={envio.id_envio}")
        
        try:
            # 2. Preparar solicitud
            request_dict = datos.model_dump()
            envio.request_json = json.dumps(request_dict, ensure_ascii=False, indent=2)
            db.commit()
            
            print(f"\n📤 ENVIANDO A API EXTERNA:")
            print(f"   URL: {ENVIOS_API_URL}")
            print(f"\n   Payload completo:")
            print(json.dumps(request_dict, ensure_ascii=False, indent=2))
            
            # 3. Enviar a API externa
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
            
            # 4. Procesar respuesta
            if response.status_code in [200, 201]:
                respuesta = response.json()
                
                try:
                    envio_resp = EnvioRespuestaSchema(**respuesta)
                    
                    # Actualizar envío con datos recibidos
                    envio.codigo_seguimiento = envio_resp.codigo_seguimiento
                    envio.estado_actual = envio_resp.estado_actual
                    envio.ubicacion_actual = envio_resp.ubicacion_actual
                    
                    # Parsear fecha
                    fecha_str = envio_resp.fecha_actualizacion
                    if fecha_str.endswith('Z'):
                        fecha_str = fecha_str.replace('Z', '+00:00')
                    envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
                    
                    # Guardar respuesta completa
                    envio.response_json = json.dumps(respuesta, ensure_ascii=False, indent=2)
                    
                    print(f"\n✅ ENVÍO CREADO EXITOSAMENTE:")
                    print(f"   ID Envío: {envio.id_envio}")
                    print(f"   Código seguimiento: {envio.codigo_seguimiento}")
                    print(f"   Estado: {envio.estado_actual}")
                    print(f"   Ubicación: {envio.ubicacion_actual}")
                    print(f"   Última actualización: {envio.fecha_actualizacion}")
                    
                except ValueError as e:
                    envio.estado_actual = "ERROR"
                    error_msg = f"Respuesta inválida. Campos esperados: id_orden_externa, codigo_seguimiento, estado_actual, ubicacion_actual, fecha_actualizacion. Error: {str(e)}"
                    envio.response_json = f"{error_msg}\n\nRespuesta:\n{response.text}"
                    print(f"\n❌ ERROR EN FORMATO DE RESPUESTA:")
                    print(f"   {error_msg}")
                    
            else:
                # Error HTTP
                envio.estado_actual = "ERROR"
                error_detail = {
                    "status_code": response.status_code,
                    "error": response.text,
                    "url": ENVIOS_API_URL
                }
                envio.response_json = json.dumps(error_detail, ensure_ascii=False, indent=2)
                
                print(f"\n❌ ERROR HTTP {response.status_code}")
                print(f"   URL: {ENVIOS_API_URL}")
                print(f"   Respuesta: {response.text}")
                
                if response.status_code == 404:
                    print(f"\n⚠️ ERROR 404 - ENDPOINT NO ENCONTRADO")
                    print(f"   1. Verifica que su API esté desplegada")
                    print(f"   2. Confirma la URL: {ENVIOS_API_URL}")
                    print(f"   3. Verifica que acepte POST")
                    
                elif response.status_code == 422:
                    print(f"\n⚠️ ERROR 422 - DATOS INVÁLIDOS")
                    print(f"   Verifica que los campos coincidan con su esquema")
                    
                elif response.status_code >= 500:
                    print(f"\n⚠️ ERROR {response.status_code} - FALLO DEL SERVIDOR")
                    print(f"   El servidor de envíos tiene un error interno")
            
            db.commit()
            db.refresh(envio)
            
            print(f"\n{'='*60}")
            print(f"🏁 PROCESO FINALIZADO - Envío ID: {envio.id_envio}")
            print(f"{'='*60}\n")
            
            return EnvioResponseSchema.model_validate(envio)
            
        except httpx.TimeoutException as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Timeout: No respondió en 30 segundos. {str(e)}"
            db.commit()
            print(f"\n❌ TIMEOUT: La API externa no respondió")
            raise HTTPException(
                status_code=504, 
                detail="Timeout: La API de envíos no respondió"
            )
            
        except httpx.RequestError as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error de conexión: {str(e)}"
            db.commit()
            print(f"\n❌ ERROR DE CONEXIÓN: {str(e)}")
            raise HTTPException(
                status_code=503, 
                detail=f"Error de conexión: {str(e)}"
            )
            
        except Exception as e:
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error inesperado: {str(e)}"
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