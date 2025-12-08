from fastapi import APIRouter, Depends, HTTPException, Query, status, Request

# Función básica de autenticación (temporal - se debe mejorar con JWT real)
def get_current_user(request: Request) -> dict:
    """
    Función básica de autenticación que maneja diferentes formatos de token
    """
    authorization = request.headers.get("authorization")
    if not authorization:
        # Para desarrollo, si no hay auth, usar usuario por defecto (cliente 10)
        return {"id_cliente": 10}

    try:
        # Intentar parsear como "Bearer <token>"
        parts = authorization.split()
        if len(parts) == 2:
            scheme, token = parts
            if scheme.lower() == "bearer":
                # Si el token es numérico, asumir que es user_id directo
                try:
                    user_id = int(token)
                    return {"id_cliente": user_id}
                except ValueError:
                    # Aquí iría la lógica de decodificar JWT
                    # Por ahora, retornar usuario por defecto
                    return {"id_cliente": 10}
        else:
            # Formato no reconocido, usar usuario por defecto
            return {"id_cliente": 10}

    except Exception:
        # En caso de error, usar usuario por defecto
        return {"id_cliente": 10}
from sqlalchemy.orm import Session
from database import get_db
from app.services.sistemaservices import SistemaServices
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
from datetime import datetime

from app.models.Cliente import ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema, ClienteUpdateSchema
from app.models.Direccion import DireccionCreateSchema, DireccionResponseSchema
from app.models.Producto import ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema, SolicitudCatalogoSchema
from app.models.Categoria import CategoriaResponseSchema, Categoria
from app.models.Carrito import CarritoAgregarSchema, CarritoResponseSchema
from app.models.Pedido import PedidoCreateSchema, PedidoResponseSchema, PagoRequestSchema, DireccionEnPedidoSchema, PedidoDetalleResponseSchema, ClienteEnPedidoSchema, ActualizarDireccionPedidoSchema
from app.services.pagoservices import PagoServices
from app.models.Pago import PagoFrontendSchema, PagoResponseSchema
from app.services.envioservices import EnvioServices
from app.models.Envio import EnvioSolicitudSchema, EnvioResponseSchema, EnvioRespuestaSchema

from app.services.ventaexternaservices import VentaExternaServices
from app.models.VentaExterna import (
    VentaExternaRegistroSchemaV2,
    VentaExternaResponseSchema,
    VentaExternaDetalleSchema
)
from app.services.clienteservices import (
    ClienteServices,
    DireccionServices,
    CarritoServices,
    PedidoServices
)
from app.services.metodopagoservices import MetodoPagoServices
from app.models.MetodoPago import MetodoPagoCreateSchema, MetodoPagoResponseSchema, MetodoPagoUpdateSchema

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
    return SistemaServices.obtener_catalogo_completo(db, store_id, category)


@router.post("/catalogo")
async def obtener_catalogo_post(
    solicitud: SolicitudCatalogoSchema,
    db: Session = Depends(get_db)
):
    return SistemaServices.obtener_catalogo_completo(
        db, 
        solicitud.store_id, 
        solicitud.category
    )


@router.get("/catalogo/all")
async def obtener_catalogo_completo_sin_filtros(db: Session = Depends(get_db)):
    return SistemaServices.obtener_catalogo_completo_sin_filtros(db)


@router.post("/pagos/procesar", response_model=PagoResponseSchema)
async def procesar_pago(datos: PagoFrontendSchema, db: Session = Depends(get_db)):
    """
    💳 Procesar pago desde el frontend
    El cliente envía solo sus datos de tarjeta.
    La tarjeta destino se agrega automáticamente en el backend.
    """
    return await PagoServices.procesar_pago_frontend(db, datos)


@router.get("/pagos/{id_pago}", response_model=PagoResponseSchema)
async def consultar_pago(id_pago: int, db: Session = Depends(get_db)):
    """Consultar información de un pago por ID"""
    return PagoServices.consultar_pago(db, id_pago)


@router.get("/pagos/pedido/{id_pedido}", response_model=List[PagoResponseSchema])
async def consultar_pagos_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """Consultar todos los pagos de un pedido"""
    return PagoServices.consultar_pagos_por_pedido(db, id_pedido)


@router.post("/envios/mock", response_model=EnvioRespuestaSchema)
async def mock_sistema_envios(datos: EnvioSolicitudSchema):
    return EnvioRespuestaSchema(
        id_orden_externa=datos.id_orden_externa,
        codigo_seguimiento=f"ENV-MOCK-{random.randint(1000, 9999)}",
        estado_actual="EN_PREPARACION",
        ubicacion_actual="Centro de distribución (MOCK)",
        fecha_actualizacion=datetime.utcnow().isoformat() + "Z"
    )


@router.post("/envios/crear", response_model=EnvioResponseSchema)
async def crear_envio(datos: EnvioSolicitudSchema, db: Session = Depends(get_db)):
    return await EnvioServices.crear_envio(db, datos)


@router.get("/envios/{id_orden_externa}", response_model=EnvioResponseSchema)
async def consultar_envio(id_orden_externa: str, db: Session = Depends(get_db)):
    return EnvioServices.consultar_envio(db, id_orden_externa)


@router.get("/envios/pedido/{id_pedido}", response_model=EnvioResponseSchema)
async def consultar_envio_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
    return EnvioServices.consultar_envio_por_pedido(db, id_pedido)


@router.post("/envios/webhook")
async def recibir_actualizacion_envio(datos: dict, db: Session = Depends(get_db)):
    return EnvioServices.actualizar_estado_webhook(db, datos)


# ==================== VENTAS EXTERNAS ====================

# Solo el endpoint que cambia - el resto del archivo routes.py permanece igual

@router.post("/ventas/registrar", status_code=status.HTTP_204_NO_CONTENT)
async def registrar_venta_externa(
    datos: VentaExternaRegistroSchemaV2, 
    db: Session = Depends(get_db)
):
    await VentaExternaServices.registrar_venta_v2(db, datos)        
    VentaExternaServices.registrar_venta_v2(db, datos)


@router.get("/ventas/externas", response_model=List[VentaExternaResponseSchema])
async def consultar_ventas_externas(
    order_id: Optional[str] = None,
    procesado: Optional[str] = Query(None, description="PROCESADO, ERROR, PENDIENTE"),
    limit: int = Query(50, le=100, description="Máximo de resultados"),
    db: Session = Depends(get_db)
):

    return VentaExternaServices.consultar_ventas_externas(
        db, order_id, procesado, limit
    )


@router.get("/ventas/orden/{order_id}", response_model=VentaExternaDetalleSchema)
async def consultar_orden_detalle(
    order_id: str,
    db: Session = Depends(get_db)
):

    return VentaExternaServices.consultar_orden_completa(db, order_id)


@router.get("/ventas/stats")
async def obtener_stats_ventas_externas(db: Session = Depends(get_db)):

    return VentaExternaServices.obtener_stats(db)


# ==================== CLIENTES ====================

@router.post("/clientes/registro", response_model=ClienteResponseSchema)
async def registrar_cliente(datos: ClienteRegistroSchema, db: Session = Depends(get_db)):
    return ClienteServices.registrar_cliente(db, datos)


@router.post("/clientes/login", response_model=ClienteResponseSchema)
async def login_cliente(datos: ClienteLoginSchema, db: Session = Depends(get_db)):
    return ClienteServices.login_cliente(db, datos)


@router.put("/clientes/{id_cliente}", response_model=ClienteResponseSchema)
async def actualizar_cliente(
    id_cliente: int,
    datos: ClienteUpdateSchema,
    db: Session = Depends(get_db)
):
    return ClienteServices.actualizar_cliente(db, id_cliente, datos)


@router.get("/clientes/{id_cliente}", response_model=ClienteResponseSchema)
async def obtener_cliente(id_cliente: int, db: Session = Depends(get_db)):
    return ClienteServices.obtener_cliente(db, id_cliente)


@router.post("/clientes/{id_cliente}/direcciones", response_model=DireccionResponseSchema)
async def agregar_direccion(
    id_cliente: int, 
    datos: DireccionCreateSchema, 
    db: Session = Depends(get_db)
):
    return DireccionServices.agregar_direccion(db, id_cliente, datos)


@router.get("/clientes/{id_cliente}/direcciones", response_model=List[DireccionResponseSchema])
async def obtener_direcciones(id_cliente: int, db: Session = Depends(get_db)):
    return DireccionServices.obtener_direcciones(db, id_cliente)


# ==================== CARRITO ====================

@router.post("/carrito/agregar", response_model=CarritoResponseSchema)
async def agregar_al_carrito(datos: CarritoAgregarSchema, db: Session = Depends(get_db)):
    return CarritoServices.agregar_al_carrito(db, datos)


@router.get("/carrito/{id_cliente}", response_model=CarritoResponseSchema)
async def obtener_carrito(id_cliente: int, db: Session = Depends(get_db)):
    return CarritoServices.obtener_carrito(db, id_cliente)


@router.delete("/carrito/item/{id_item}")
async def eliminar_item_carrito(id_item: int, id_cliente: int = Query(...), db: Session = Depends(get_db)):
    return CarritoServices.eliminar_item(db, id_item, id_cliente)


@router.delete("/carrito/{id_cliente}/vaciar")
async def vaciar_carrito(id_cliente: int, db: Session = Depends(get_db)):
    return CarritoServices.vaciar_carrito(db, id_cliente)


# ==================== PEDIDOS ====================

@router.post("/pedidos/crear", response_model=PedidoResponseSchema)
async def crear_pedido_desde_carrito(
    id_cliente: int,
    id_direccion: int,
    db: Session = Depends(get_db)
):
    return PedidoServices.crear_pedido_desde_carrito(db, id_cliente, id_direccion)


@router.get("/pedidos/{id_pedido}", response_model=PedidoResponseSchema)
async def obtener_pedido(id_pedido: int, db: Session = Depends(get_db)):
    return PedidoServices.obtener_pedido(db, id_pedido)


@router.get("/pedidos/cliente/{id_cliente}", response_model=List[PedidoResponseSchema])
async def listar_pedidos_cliente(id_cliente: int, db: Session = Depends(get_db)):
    return PedidoServices.listar_pedidos_cliente(db, id_cliente)


@router.put("/pedidos/{id_pedido}/estado")
async def actualizar_estado_pedido(
    id_pedido: int,
    nuevo_estado: str,
    db: Session = Depends(get_db)
):
    return PedidoServices.actualizar_estado_pedido(db, id_pedido, nuevo_estado)


# ==================== MÉTODOS DE PAGO ====================

@router.get("/clientes/{id_cliente}/tarjetas", response_model=List[MetodoPagoResponseSchema])
async def obtener_tarjetas_cliente(id_cliente: int, db: Session = Depends(get_db)):
    return MetodoPagoServices.obtener_tarjetas_cliente(db, id_cliente)


@router.post("/clientes/{id_cliente}/tarjetas", response_model=MetodoPagoResponseSchema)
async def agregar_tarjeta(
    id_cliente: int,
    datos: MetodoPagoCreateSchema,
    db: Session = Depends(get_db)
):
    return MetodoPagoServices.agregar_tarjeta(db, id_cliente, datos)


@router.put("/clientes/{id_cliente}/tarjetas/{id_tarjeta}", response_model=MetodoPagoResponseSchema)
async def actualizar_tarjeta(
    id_cliente: int,
    id_tarjeta: int,
    datos: MetodoPagoUpdateSchema,
    db: Session = Depends(get_db)
):
    return MetodoPagoServices.actualizar_tarjeta(db, id_cliente, id_tarjeta, datos)


@router.delete("/clientes/{id_cliente}/tarjetas/{id_tarjeta}")
async def eliminar_tarjeta(
    id_cliente: int,
    id_tarjeta: int,
    db: Session = Depends(get_db)
):
    return MetodoPagoServices.eliminar_tarjeta(db, id_cliente, id_tarjeta)


@router.put("/clientes/{id_cliente}/tarjetas/{id_tarjeta}/predeterminada", response_model=MetodoPagoResponseSchema)
async def establecer_tarjeta_predeterminada(
    id_cliente: int,
    id_tarjeta: int,
    db: Session = Depends(get_db)
):
    return MetodoPagoServices.establecer_tarjeta_predeterminada(db, id_cliente, id_tarjeta)

@router.get("/pedidos/{id_pedido}/detalle", response_model=PedidoDetalleResponseSchema)
async def obtener_detalle_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """Obtener detalle completo del pedido con información de cliente y dirección"""
    return PedidoServices.obtener_detalle_pedido(db, id_pedido)

@router.patch("/pedidos/{id_pedido}/direccion")
async def actualizar_direccion_pedido(
    id_pedido: int,
    datos: ActualizarDireccionPedidoSchema,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar la dirección de envío de un pedido
    También actualiza en el servicio externo de envíos si existe un envío creado
    """
    return PedidoServices.actualizar_direccion_pedido(
        db, id_pedido, current_user["id_cliente"], datos.dict()
    )