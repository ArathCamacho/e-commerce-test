from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.models.Pago import PagoIniciarSchema, PagoFrontendSchema, PagoResponseSchema
from app.services.envioservices import EnvioServices
from app.models.Envio import EnvioSolicitudSchema, EnvioResponseSchema, EnvioRespuestaSchema

from app.services.ventaexternaservices import VentaExternaServices
from app.models.VentaExterna import VentaExternaRegistroSchema, VentaExternaResponseSchema
from app.services.clienteservices import (
    ClienteServices, 
    DireccionServices, 
    CarritoServices, 
    PedidoServices
)

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


# Endpoint NUEVO para el frontend (sin tarjeta destino)
@router.post("/pagos/procesar", response_model=PagoResponseSchema)
async def procesar_pago_desde_frontend(
    datos: PagoFrontendSchema,  # ← Usa el nuevo schema
    db: Session = Depends(get_db)
):
    """
    Procesa un pago desde el frontend.
    El cliente solo envía su tarjeta, tu tarjeta destino se agrega automáticamente.
    """
    return await PagoServices.procesar_pago_frontend(db, datos)


# Endpoint INTERNO (con tarjeta destino explícita) - solo para testing/admin
@router.post("/pagos/procesar-completo", response_model=PagoResponseSchema)
async def procesar_pago_completo(
    datos: PagoIniciarSchema,
    db: Session = Depends(get_db)
):
    """
    Procesa un pago con tarjeta destino explícita.
    Solo para pruebas o uso administrativo.
    """
    return await PagoServices.procesar_pago(db, datos)


@router.get("/pagos/{id_pago}", response_model=PagoResponseSchema)
async def consultar_pago(id_pago: int, db: Session = Depends(get_db)):
    return PagoServices.consultar_pago(db, id_pago)


@router.get("/pagos/pedido/{id_pedido}", response_model=List[PagoResponseSchema])
async def consultar_pagos_por_pedido(id_pedido: int, db: Session = Depends(get_db)):
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


@router.get("/envios/{id_envio}", response_model=EnvioResponseSchema)
async def consultar_envio(id_envio: int, db: Session = Depends(get_db)):

    return EnvioServices.consultar_envio(db, id_envio)


@router.get("/envios/pedido/{id_pedido}", response_model=EnvioResponseSchema)
async def consultar_envio_por_pedido(id_pedido: int, db: Session = Depends(get_db)):

    return EnvioServices.consultar_envio_por_pedido(db, id_pedido)


@router.post("/envios/webhook")
async def recibir_actualizacion_envio(datos: dict, db: Session = Depends(get_db)):

    return EnvioServices.actualizar_estado_webhook(db, datos)

@router.post("/ventas/registrar", response_model=VentaExternaResponseSchema)
async def registrar_venta_externa(
    datos: VentaExternaRegistroSchema, 
    db: Session = Depends(get_db)
):
    return VentaExternaServices.registrar_venta(db, datos)


@router.get("/ventas/externas", response_model=List[VentaExternaResponseSchema])
async def consultar_ventas_externas(
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return VentaExternaServices.consultar_ventas_externas(db, order_id)


@router.post("/clientes/registro", response_model=ClienteResponseSchema)
async def registrar_cliente(datos: ClienteRegistroSchema, db: Session = Depends(get_db)):
    return ClienteServices.registrar_cliente(db, datos)


@router.post("/clientes/login", response_model=ClienteResponseSchema)
async def login_cliente(datos: ClienteLoginSchema, db: Session = Depends(get_db)):
    return ClienteServices.login_cliente(db, datos)


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