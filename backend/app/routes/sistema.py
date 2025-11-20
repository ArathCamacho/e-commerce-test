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
from app.models.Envio import EnvioIniciarSchema, EnvioResponseSchema

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
async def crear_envio(datos: EnvioIniciarSchema, db: Session = Depends(get_db)):
    """
    📦 Crear solicitud de envío
    
    Body: {
        "id_pedido": 15
    }
    
    Respuesta:
    {
        "id_envio": 1,
        "id_pedido": 15,
        "id_orden_externa": "ECM-2024-00015",
        "codigo_seguimiento": "ENV-ABC123",
        "estado_actual": "EN_PREPARACION",
        "ubicacion_actual": "Centro de distribución",
        "fecha_actualizacion": "2024-11-19T10:30:00"
    }
    """
    return await EnvioServices.crear_envio(db, datos)


@router.get("/envios/{id_envio}", response_model=EnvioResponseSchema)
async def consultar_envio(id_envio: int, db: Session = Depends(get_db)):
    """🔍 Consultar estado de un envío por ID"""
    return EnvioServices.consultar_envio(db, id_envio)


@router.get("/envios/pedido/{id_pedido}", response_model=EnvioResponseSchema)
async def consultar_envio_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar envío de un pedido
    
    Ejemplo: GET /api/envios/pedido/15
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