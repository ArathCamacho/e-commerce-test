import httpx
import json
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.Envio import (
    Envio, 
    EnvioIniciarSchema, 
    EnvioSolicitudSchema, 
    EnvioRespuestaSchema, 
    EnvioResponseSchema,
    ProductoEnvioSchema,
    DatosClienteEnvioSchema
)
from app.models.Pedido import Pedido
from app.models.Cliente import Cliente
from app.models.Direccion import Direccion

ENVIOS_API_URL = "https://gestion-envios-sz3x.onrender.com/api/envios/crear"


class EnvioServices:
    
    @staticmethod
    async def crear_envio(db: Session, datos: EnvioIniciarSchema):
        """
        📦 CREAR SOLICITUD DE ENVÍO
        
        Flujo:
        1. Buscar pedido con sus items y productos
        2. Validar cliente y dirección
        3. Construir JSON (SOL_ENV)
        4. Enviar a API externa
        5. Guardar respuesta (EDO_ENV)
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO CREACIÓN DE ENVÍO PARA PEDIDO {datos.id_pedido}")
        print(f"{'='*60}\n")
        
        # 1. Buscar pedido con EAGER LOADING (items + productos)
        pedido = db.query(Pedido).options(
            joinedload(Pedido.items).joinedload('producto')
        ).filter(Pedido.id_pedido == datos.id_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail=f"❌ Pedido {datos.id_pedido} no encontrado")
        
        print(f"✅ Pedido encontrado: ID={pedido.id_pedido}, Total={pedido.total}")
        print(f"   Cliente ID: {pedido.id_cliente}")
        print(f"   Dirección ID: {pedido.id_direccion}")
        print(f"   Items: {len(pedido.items) if pedido.items else 0}")
        
        # Validar que tenga items
        if not pedido.items or len(pedido.items) == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"❌ El pedido {datos.id_pedido} no tiene productos (tabla pedido_item vacía)"
            )
        
        # 2. Obtener cliente
        cliente = db.query(Cliente).filter(Cliente.id_cliente == pedido.id_cliente).first()
        if not cliente:
            raise HTTPException(
                status_code=404, 
                detail=f"❌ Cliente {pedido.id_cliente} no encontrado"
            )
        
        print(f"✅ Cliente encontrado: {cliente.nombre} {cliente.apellido}")
        print(f"   Email: {cliente.correo}")
        print(f"   Teléfono: {cliente.telefono}")
        
        # 3. Obtener dirección
        direccion = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
        if not direccion:
            raise HTTPException(
                status_code=404, 
                detail=f"❌ Dirección {pedido.id_direccion} no encontrada"
            )
        
        print(f"✅ Dirección encontrada: {direccion.calle}")
        print(f"   Ciudad: {direccion.ciudad}, {direccion.estado} {direccion.codigo_postal}")
        
        # 4. Generar ID único
        id_orden_externa = f"ECM-{datetime.now().year}-{pedido.id_pedido:05d}"
        print(f"✅ ID orden externa generado: {id_orden_externa}")
        
        # 5. Preparar datos del cliente
        datos_cliente = DatosClienteEnvioSchema(
            nombre=f"{cliente.nombre} {cliente.apellido}",
            telefono=cliente.telefono or "Sin teléfono",
            email=cliente.correo,
            direccion_completa=direccion.calle,
            ciudad=direccion.ciudad,
            estado=direccion.estado,
            codigo_postal=direccion.codigo_postal
        )
        
        print(f"\n📋 Datos del cliente preparados:")
        print(f"   Nombre: {datos_cliente.nombre}")
        print(f"   Email: {datos_cliente.email}")
        
        # 6. Preparar lista de productos
        productos = []
        print(f"\n📦 Procesando {len(pedido.items)} productos:")
        
        for idx, item in enumerate(pedido.items, 1):
            # Validar que el item tenga producto asociado
            if not item.producto:
                raise HTTPException(
                    status_code=500,
                    detail=f"❌ El item {item.id_pedido_item} no tiene producto asociado (verifica relaciones)"
                )
            
            producto_envio = ProductoEnvioSchema(
                id_producto=item.id_producto,
                nombre=item.producto.nombre,
                cantidad=item.cantidad,
                precio=float(item.precio_unitario)
            )
            productos.append(producto_envio)
            
            print(f"   {idx}. {item.producto.nombre}")
            print(f"      ID: {item.id_producto} | Cant: {item.cantidad} | Precio: ${item.precio_unitario}")
        
        # 7. Crear registro en BD (estado PENDIENTE)
        envio = Envio(
            id_pedido=pedido.id_pedido,
            id_orden_externa=id_orden_externa,
            id_orden_original=pedido.id_pedido,
            servicio_origen="ecommerce",
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        print(f"\n✅ Registro de envío creado en BD: ID={envio.id_envio}")
        
        try:
            # 8. Construir solicitud (SOL_ENV)
            solicitud = EnvioSolicitudSchema(
                id_orden_externa=id_orden_externa,
                id_orden_original=pedido.id_pedido,
                servicio_origen="ecommerce",
                datos_cliente=datos_cliente,
                productos=productos
            )
            
            # Guardar solicitud (auditoría)
            request_dict = solicitud.model_dump()
            envio.request_json = json.dumps(request_dict, ensure_ascii=False, indent=2)
            db.commit()
            
            print(f"\n📤 ENVIANDO A API EXTERNA:")
            print(f"   URL: {ENVIOS_API_URL}")
            print(f"   Payload:")
            print(json.dumps(request_dict, ensure_ascii=False, indent=2))
            
            # 9. Enviar a API externa
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    ENVIOS_API_URL,
                    json=request_dict,
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"\n📥 RESPUESTA DE API EXTERNA:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Body: {response.text[:500]}")  # Primeros 500 chars
            
            # 10. Procesar respuesta
            if response.status_code in [200, 201]:
                respuesta = response.json()
                
                # Validar estructura de respuesta
                try:
                    envio_resp = EnvioRespuestaSchema(**respuesta)
                    
                    # Actualizar envío con datos recibidos
                    envio.codigo_seguimiento = envio_resp.codigo_seguimiento
                    envio.estado_actual = envio_resp.estado_actual
                    envio.ubicacion_actual = envio_resp.ubicacion_actual
                    
                    # Parsear fecha
                    fecha_str = envio_resp.fecha_actualizacion.replace('Z', '+00:00')
                    envio.fecha_actualizacion = datetime.fromisoformat(fecha_str)
                    
                    # Guardar respuesta completa
                    envio.response_json = json.dumps(respuesta, ensure_ascii=False, indent=2)
                    
                    print(f"\n✅ ENVÍO CREADO EXITOSAMENTE:")
                    print(f"   Código seguimiento: {envio.codigo_seguimiento}")
                    print(f"   Estado: {envio.estado_actual}")
                    
                except Exception as e:
                    # Error al parsear respuesta
                    envio.estado_actual = "ERROR"
                    envio.response_json = f"Error al parsear respuesta: {str(e)}\n\nRespuesta: {response.text}"
                    print(f"\n❌ ERROR AL PARSEAR RESPUESTA: {str(e)}")
                    
            else:
                # Error HTTP de la API
                envio.estado_actual = "ERROR"
                error_detail = {
                    "status_code": response.status_code,
                    "error": response.text
                }
                envio.response_json = json.dumps(error_detail, ensure_ascii=False, indent=2)
                print(f"\n❌ ERROR HTTP {response.status_code}: {response.text}")
            
            db.commit()
            db.refresh(envio)
            
            print(f"\n{'='*60}")
            print(f"🏁 PROCESO FINALIZADO - Envío ID: {envio.id_envio}")
            print(f"{'='*60}\n")
            
            return EnvioResponseSchema.model_validate(envio)
            
        except httpx.TimeoutException as e:
            # Timeout en la llamada
            envio.estado_actual = "ERROR"
            envio.response_json = f"Timeout: La API no respondió en 30 segundos. {str(e)}"
            db.commit()
            print(f"\n❌ TIMEOUT: La API externa no respondió")
            raise HTTPException(status_code=504, detail="Timeout: La API de envíos no respondió")
            
        except httpx.RequestError as e:
            # Error de red/conexión
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error de conexión: {str(e)}"
            db.commit()
            print(f"\n❌ ERROR DE CONEXIÓN: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Error de conexión con API de envíos: {str(e)}")
            
        except Exception as e:
            # Cualquier otro error
            envio.estado_actual = "ERROR"
            envio.response_json = f"Error inesperado: {str(e)}"
            db.commit()
            print(f"\n❌ ERROR INESPERADO: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error al crear envío: {str(e)}")
    
    
    @staticmethod
    def consultar_envio(db: Session, id_envio: int):
        """🔍 Consultar estado de un envío por ID"""
        envio = db.query(Envio).filter(Envio.id_envio == id_envio).first()
        if not envio:
            raise HTTPException(status_code=404, detail="Envío no encontrado")
        
        # Debug si está en error
        if envio.estado_actual == "ERROR":
            print(f"\n⚠️ ENVÍO {id_envio} EN ERROR:")
            print(f"Request enviado:\n{envio.request_json}\n")
            print(f"Response recibido:\n{envio.response_json}\n")
        
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def consultar_envio_por_pedido(db: Session, id_pedido: int):
        """🔍 Consultar envío de un pedido específico"""
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()
        if not envio:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay envío registrado para el pedido {id_pedido}"
            )
        return EnvioResponseSchema.model_validate(envio)