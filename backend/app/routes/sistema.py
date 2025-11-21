from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.sistemaservices import SistemaServices
from pydantic import BaseModel
from typing import List, Optional

from app.models.Cliente import ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema
from app.models.Direccion import DireccionCreateSchema, DireccionResponseSchema
from app.models.Producto import ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema, SolicitudCatalogoSchema
from app.models.Categoria import CategoriaResponseSchema, Categoria
from app.models.Carrito import CarritoAgregarSchema, CarritoResponseSchema
from app.models.Pedido import PedidoCreateSchema, PedidoResponseSchema, PagoRequestSchema
from app.services.pagoservices import PagoServices
from app.models.Pago import PagoIniciarSchema, PagoResponseSchema
from app.services.envioservices import EnvioServices
from app.models.Envio import EnvioSolicitudSchema, EnvioResponseSchema

from app.services.ventaexternaservices import VentaExternaServices
from app.models.VentaExterna import VentaExternaRegistroSchema, VentaExternaResponseSchema
router = APIRouter()

class VerificarDisponibilidadSchema(BaseModel):
    """Schema para verificar si hay stock suficiente"""
    id_producto: int
    cantidad_solicitada: int


@router.post("/productos/verificar-disponibilidad")
async def verificar_disponibilidad(
    data: VerificarDisponibilidadSchema, 
    db: Session = Depends(get_db)
):
    """
    🔍 VERIFICAR DISPONIBILIDAD DE PRODUCTO
    
    Revisa si hay stock suficiente para surtir cierta cantidad.
    
    Ejemplo de uso:
    POST /api/productos/verificar-disponibilidad
    Body:
    {
        "id_producto": 8,
        "cantidad_solicitada": 5
    }
    
    Respuesta:
    {
        "id_producto": 8,
        "stock": 100
    }
    """
    return SistemaServices.verificar_disponibilidad_producto(
        db,
        data.id_producto,
        data.cantidad_solicitada
    )


@router.get("/catalogo")
async def obtener_catalogo(
    store_id: int = 1,
    category: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    �' ENDPOINT PRINCIPAL DEL CATÁLOGO PARA API DISTRIBUIDA
    
    Este es el endpoint que otros equipos consultarán.
    
    Parámetros (Query Params):
    - store_id: ID de tu tienda (default: 1)
    - category: ID de categoría (opcional)
    
    Ejemplos:
    
    1. Obtener TODO el catálogo de la tienda 1:
       GET /api/catalogo?store_id=1
    
    2. Obtener solo productos de categoría 2 (Ropa):
       GET /api/catalogo?store_id=1&category=2
    
    3. Sin parámetros (usa store_id=1 por defecto):
       GET /api/catalogo
    
    Respuesta (Array de productos):
    [
        {
            "store_id": 1,
            "id": 8,
            "nombre": "Playera Básica Negra",
            "description": "Playera de algodón 100%",
            "precio": 199.99,
            "talla": "M",
            "color": "Negro",
            "stock": 100,
            "duracion_minutos": null
        },
        {
            "store_id": 1,
            "id": 1,
            "nombre": "Laptop HP",
            "description": "Laptop gaming",
            "precio": 12999.99,
            "talla": null,
            "color": null,
            "stock": 15,
            "duracion_minutos": null
        }
    ]
    """
    return SistemaServices.obtener_catalogo_completo(db, store_id, category)


@router.post("/catalogo")
async def obtener_catalogo_post(
    solicitud: SolicitudCatalogoSchema,
    db: Session = Depends(get_db)
):
    """
    �' ENDPOINT DEL CATÁLOGO (Método POST)
    
    Alternativa si otros equipos prefieren enviar los datos por POST
    
    Body:
    {
        "store_id": 1,
        "category": 2
    }
    
    Respuesta igual que el GET (array de productos)
    """
    return SistemaServices.obtener_catalogo_completo(
        db, 
        solicitud.store_id, 
        solicitud.category
    )
@router.post("/pagos/procesar", response_model=PagoResponseSchema)
async def procesar_pago(datos: PagoIniciarSchema, db: Session = Depends(get_db)):
    """
    💳 Procesar pago con banco
    
    Body:
    {
        "numero_tarjeta_origen": "1234 5678 9012 3456",
        "nombre_cliente": "Juan Perez",
        "mes_exp": 12,
        "anio_exp": 2027,
        "cvv": "123",
        "monto": 199.99,
        "moneda": "MXN",
        "id_pedido": 1
    }
    
    Respuesta:
    {
        "id_pago": 1,
        "estado": "APROBADO",
        "monto": 199.99,
        "id_transaccion": "TXN-123456",
        "firma": "abc123xyz"
    }
    """
    return await PagoServices.procesar_pago(db, datos)

@router.get("/pagos/{id_pago}", response_model=PagoResponseSchema)
async def consultar_pago(id_pago: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar estado de un pago por ID
    
    Ejemplo: GET /api/pagos/1
    """
    return PagoServices.consultar_pago(db, id_pago)


@router.get("/pagos/pedido/{id_pedido}", response_model=List[PagoResponseSchema])
async def consultar_pagos_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar todos los pagos de un pedido
    
    Ejemplo: GET /api/pagos/pedido/1
    
    Respuesta (Array):
    [
        {
            "id_pago": 1,
            "estado": "RECHAZADO",
            "monto": 199.99,
            "id_transaccion": "TXN-001",
            "firma": "abc123"
        },
        {
            "id_pago": 2,
            "estado": "APROBADO",
            "monto": 199.99,
            "id_transaccion": "TXN-002",
            "firma": "xyz789"
        }
    ]
    """
    return PagoServices.consultar_pagos_por_pedido(db, id_pedido)

@router.post("/envios/crear", response_model=EnvioResponseSchema)
async def crear_envio(datos: EnvioSolicitudSchema, db: Session = Depends(get_db)):
    """
    📦 CREAR SOLICITUD DE ENVÍO (RECIBE DATOS COMPLETOS)
    
    Ahora este endpoint recibe TODOS los datos directamente,
    no solo el id_pedido.
    
    Body completo:
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
    
    Respuesta exitosa (5 campos + 2 internos):
    {
      "id_envio": 10,                           // ← Tu ID interno
      "id_pedido": 2,                           // ← Referencia al pedido
      "id_orden_externa": "ECM-2025-00002",     // ← Del request
      "codigo_seguimiento": "ENV-ABC123",       // ← Del servidor de envíos
      "estado_actual": "EN_PREPARACION",        // ← Del servidor de envíos
      "ubicacion_actual": "Centro distribución", // ← Del servidor de envíos
      "fecha_actualizacion": "2025-11-20T10:30:00" // ← Del servidor de envíos
    }
    
    Respuesta con error:
    {
      "id_envio": 10,
      "id_pedido": 2,
      "id_orden_externa": "ECM-2025-00002",
      "codigo_seguimiento": null,
      "estado_actual": "ERROR",
      "ubicacion_actual": null,
      "fecha_actualizacion": null
    }
    (Revisar response_json en BD para ver el error exacto)
    """
    return await EnvioServices.crear_envio(db, datos)


@router.get("/envios/{id_envio}", response_model=EnvioResponseSchema)
async def consultar_envio(id_envio: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar estado de un envío por ID
    
    Ejemplo: GET /api/envios/10
    
    Si el envío está en ERROR, revisa los logs del servidor
    para ver qué falló (request_json y response_json).
    """
    return EnvioServices.consultar_envio(db, id_envio)


@router.get("/envios/pedido/{id_pedido}", response_model=EnvioResponseSchema)
async def consultar_envio_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar envío de un pedido
    
    Ejemplo: GET /api/envios/pedido/2
    """
    return EnvioServices.consultar_envio_por_pedido(db, id_pedido)

@router.get("/catalogo/all")
async def obtener_catalogo_completo_sin_filtros(db: Session = Depends(get_db)):
    """
    🛒 CATÁLOGO COMPLETO SIN FILTROS
    
    Devuelve TODOS los productos activos sin necesidad de parámetros.
    
    Ejemplo de uso:
    GET /api/catalogo/all
    
    Respuesta (Array de todos los productos):
    [
        {
            "store_id": 1,
            "id": 8,
            "nombre": "Playera Básica Negra",
            "description": "Playera de algodón 100%",
            "precio": 199.99,
            "talla": "M",
            "color": "Negro",
            "stock": 100,
            "duracion_minutos": null
        },
        {
            "store_id": 1,
            "id": 1,
            "nombre": "Laptop HP",
            "description": "Laptop gaming",
            "precio": 12999.99,
            "talla": null,
            "color": null,
            "stock": 15,
            "duracion_minutos": null
        },
        {
            "store_id": 2,
            "id": 25,
            "nombre": "Producto de otra tienda",
            "description": "...",
            "precio": 599.99,
            "talla": "L",
            "color": "Azul",
            "stock": 50,
            "duracion_minutos": null
        }
    ]
    """
    return SistemaServices.obtener_catalogo_completo_sin_filtros(db)

@router.post("/ventas/registrar", response_model=VentaExternaResponseSchema)
async def registrar_venta_externa(
    datos: VentaExternaRegistroSchema, 
    db: Session = Depends(get_db)
):
    """
    🛍️ WEBHOOK: Registrar venta externa
    
    Este endpoint lo llamarán otros sistemas cuando vendan tus productos.
    
    Body:
    {
        "id": 1,
        "order_id": "ORD-EXT-12345",
        "store_id": 1,
        "product_external_id": 1,
        "product_name": "Playera Básica",
        "price": 199.99,
        "quantity": 2,
        "size": "M",
        "color": "Negro",
        "options": null,
        "created_at": "2025-11-20T10:30:00",
        "payment_status": "PAID"
    }
    
    Respuesta:
    {
        "id_venta_externa": 1,
        "order_id": "ORD-EXT-12345",
        "product_name": "Playera Básica",
        "quantity": 2,
        "price": 199.99,
        "payment_status": "PAID",
        "procesado": "PROCESADO",
        "id_pedido_generado": 15,
        "fecha_registro": "2025-11-20T10:30:00"
    }
    
    Lo que hace:
    1. ✅ Verifica que la orden no esté duplicada
    2. ✅ Valida que el producto exista en tu catálogo
    3. ✅ Crea un pedido automático en tu sistema
    4. ✅ Descuenta el stock del producto
    5. ✅ Guarda el registro completo de la venta
    """
    return VentaExternaServices.registrar_venta(db, datos)


@router.get("/ventas/externas", response_model=List[VentaExternaResponseSchema])
async def consultar_ventas_externas(
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🔍 Consultar ventas externas registradas
    
    Ejemplos:
    - GET /api/ventas/externas  (últimas 50 ventas)
    - GET /api/ventas/externas?order_id=ORD-EXT-12345  (una orden específica)
    """
    return VentaExternaServices.consultar_ventas_externas(db, order_id)

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