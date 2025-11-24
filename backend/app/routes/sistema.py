from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.sistemaservices import SistemaServices
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime

from app.models.Cliente import ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema
from app.models.Direccion import DireccionCreateSchema, DireccionResponseSchema
from app.models.Producto import ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema, SolicitudCatalogoSchema
from app.models.Categoria import CategoriaResponseSchema, Categoria
from app.models.Carrito import CarritoAgregarSchema, CarritoResponseSchema
from app.models.Pedido import PedidoCreateSchema, PedidoResponseSchema, PagoRequestSchema
from app.services.pagoservices import PagoServices
from app.models.Pago import PagoIniciarSchema, PagoResponseSchema
from app.services.envioservices import EnvioServices
from app.models.Envio import EnvioSolicitudSchema, EnvioResponseSchema, EnvioRespuestaSchema

from app.services.ventaexternaservices import VentaExternaServices
from app.models.VentaExterna import VentaExternaRegistroSchema, VentaExternaResponseSchema

router = APIRouter()


class VerificarDisponibilidadSchema(BaseModel):
    """Schema para verificar si hay stock suficiente"""
    id_producto: int
    cantidad_solicitada: int


# ============================================
# ENDPOINTS DE PRODUCTOS Y CATÁLOGO
# ============================================

@router.post("/productos/verificar-disponibilidad")
async def verificar_disponibilidad(
    data: VerificarDisponibilidadSchema, 
    db: Session = Depends(get_db)
):
    """
    🔍 VERIFICAR DISPONIBILIDAD DE PRODUCTO
    
    Revisa si hay stock suficiente para surtir cierta cantidad.
    
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
    🛒 ENDPOINT PRINCIPAL DEL CATÁLOGO PARA API DISTRIBUIDA
    
    Parámetros (Query Params):
    - store_id: ID de tu tienda (default: 1)
    - category: ID de categoría (opcional)
    
    Ejemplos:
    - GET /api/catalogo?store_id=1
    - GET /api/catalogo?store_id=1&category=2
    """
    return SistemaServices.obtener_catalogo_completo(db, store_id, category)


@router.post("/catalogo")
async def obtener_catalogo_post(
    solicitud: SolicitudCatalogoSchema,
    db: Session = Depends(get_db)
):
    """
    🛒 ENDPOINT DEL CATÁLOGO (Método POST)
    
    Body:
    {
        "store_id": 1,
        "category": 2
    }
    """
    return SistemaServices.obtener_catalogo_completo(
        db, 
        solicitud.store_id, 
        solicitud.category
    )


@router.get("/catalogo/all")
async def obtener_catalogo_completo_sin_filtros(db: Session = Depends(get_db)):
    """
    🛒 CATÁLOGO COMPLETO SIN FILTROS
    
    Devuelve TODOS los productos activos.
    """
    return SistemaServices.obtener_catalogo_completo_sin_filtros(db)


# ============================================
# ENDPOINTS DE PAGOS
# ============================================

@router.post("/pagos/procesar", response_model=PagoResponseSchema)
async def procesar_pago(datos: PagoIniciarSchema, db: Session = Depends(get_db)):
    """
    💳 PROCESAR PAGO CON EL BANCO
    
    Body:
    {
        "numero_tarjeta_origen": "5555555555554444",
        "numero_tarjeta_destino": "4111111111111111",
        "nombre_cliente": "Juan Pérez",
        "mes_exp": 12,
        "anio_exp": 2030,
        "cvv": "456",
        "monto": 199.99,
        "moneda": "MXN",
        "tipo": "venta",
        "id_pedido": 1
    }
    """
    return await PagoServices.procesar_pago(db, datos)


@router.get("/pagos/{id_pago}", response_model=PagoResponseSchema)
async def consultar_pago(id_pago: int, db: Session = Depends(get_db)):
    """
    🔍 CONSULTAR ESTADO DE UN PAGO
    
    Ejemplo: GET /api/pagos/1
    """
    return PagoServices.consultar_pago(db, id_pago)


@router.get("/pagos/pedido/{id_pedido}", response_model=List[PagoResponseSchema])
async def consultar_pagos_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    🔍 CONSULTAR TODOS LOS PAGOS DE UN PEDIDO
    
    Ejemplo: GET /api/pagos/pedido/1
    """
    return PagoServices.consultar_pagos_por_pedido(db, id_pedido)
# ============================================
# ENDPOINTS DE ENVÍOS
# ============================================

@router.post("/envios/mock", response_model=EnvioRespuestaSchema)
async def mock_sistema_envios(datos: EnvioSolicitudSchema):
    """
    🧪 MOCK - Simula el servidor del otro equipo (SOLO DESARROLLO)
    
    Este endpoint NO lo usas directamente.
    Es llamado internamente por el service cuando está en modo desarrollo.
    """
    return EnvioRespuestaSchema(
        id_orden_externa=datos.id_orden_externa,
        codigo_seguimiento=f"ENV-MOCK-{random.randint(1000, 9999)}",
        estado_actual="EN_PREPARACION",
        ubicacion_actual="Centro de distribución (MOCK)",
        fecha_actualizacion=datetime.utcnow().isoformat() + "Z"
    )


@router.post("/envios/crear", response_model=EnvioResponseSchema)
async def crear_envio(datos: EnvioSolicitudSchema, db: Session = Depends(get_db)):
    """
    📦 CREAR ENVÍO - ENDPOINT PRINCIPAL
    
    Body:
    {
        "id_orden_externa": "ECM-2025-00001",
        "id_orden_original": 15,
        "servicio_origen": "ecommerce",
        "datos_cliente": {
            "nombre": "Juan Pérez",
            "telefono": "6621234567",
            "email": "juan@example.com",
            "direccion_completa": "Calle Sol #45",
            "ciudad": "Hermosillo",
            "estado": "Sonora",
            "codigo_postal": "83000"
        },
        "productos": [
            {
                "id_producto": 1,
                "nombre": "Playera",
                "cantidad": 2,
                "precio": 199.99
            }
        ]
    }
    
    Respuesta:
    {
        "id_envio": 10,
        "id_pedido": 15,
        "id_orden_externa": "ECM-2025-00001",
        "codigo_seguimiento": "ENV-MOCK-1234",
        "estado_actual": "EN_PREPARACION",
        "ubicacion_actual": "Centro de distribución",
        "fecha_actualizacion": "2025-11-22T10:30:00"
    }
    """
    return await EnvioServices.crear_envio(db, datos)


@router.get("/envios/{id_envio}", response_model=EnvioResponseSchema)
async def consultar_envio(id_envio: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar estado de un envío por ID
    
    Ejemplo: GET /api/envios/10
    """
    return EnvioServices.consultar_envio(db, id_envio)


@router.get("/envios/pedido/{id_pedido}", response_model=EnvioResponseSchema)
async def consultar_envio_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """
    🔍 Consultar envío de un pedido
    
    Ejemplo: GET /api/envios/pedido/2
    """
    return EnvioServices.consultar_envio_por_pedido(db, id_pedido)


@router.post("/envios/webhook")
async def recibir_actualizacion_envio(datos: dict, db: Session = Depends(get_db)):
    """
    🔔 WEBHOOK - Recibe actualizaciones del sistema de envíos
    
    Este endpoint lo llama el OTRO EQUIPO cuando hay cambios en el envío.
    
    Body esperado:
    {
        "id_orden_externa": "003",
        "codigo_seguimiento": "ENV-123",
        "estado_actual": "EN_TRANSITO",
        "ubicacion_actual": "Guadalajara",
        "fecha_actualizacion": "2025-11-23T10:30:00Z"
    }
    """
    return EnvioServices.actualizar_estado_webhook(db, datos)


# ============================================
# ENDPOINTS DE VENTAS EXTERNAS
# ============================================

@router.post("/ventas/registrar", response_model=VentaExternaResponseSchema)
async def registrar_venta_externa(
    datos: VentaExternaRegistroSchema, 
    db: Session = Depends(get_db)
):
    """
    🛍️ WEBHOOK: Registrar venta externa
    
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
    - GET /api/ventas/externas
    - GET /api/ventas/externas?order_id=ORD-EXT-12345
    """
    return VentaExternaServices.consultar_ventas_externas(db, order_id)