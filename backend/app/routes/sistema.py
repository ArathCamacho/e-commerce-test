from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.sistemaservices import SistemaServices
from pydantic import BaseModel
from typing import List

from app.models.Cliente import ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema
from app.models.Direccion import DireccionCreateSchema, DireccionResponseSchema
from app.models.Producto import ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema
from app.models.Categoria import CategoriaResponseSchema
from app.models.Carrito import CarritoAgregarSchema, CarritoResponseSchema
from app.models.Pedido import PedidoCreateSchema, PedidoResponseSchema, PagoRequestSchema
from pydantic import BaseModel

router = APIRouter()


@router.post("/clientes/registro", response_model=ClienteResponseSchema)
async def registrar_cliente(data: ClienteRegistroSchema, db: Session = Depends(get_db)):
    """Registra un nuevo cliente"""
    return SistemaServices.registrar_cliente(db, data)


@router.post("/clientes/login", response_model=ClienteResponseSchema)
async def login_cliente(data: ClienteLoginSchema, db: Session = Depends(get_db)):
    """Login de cliente"""
    return SistemaServices.login_cliente(db, data.correo, data.contrasena)

@router.post("/clientes/{id_cliente}/direcciones", response_model=DireccionResponseSchema)
async def crear_direccion(id_cliente: int, data: DireccionCreateSchema, db: Session = Depends(get_db)):
    """Crea una nueva dirección para un cliente"""
    return SistemaServices.crear_direccion(db, id_cliente, data)


@router.get("/clientes/{id_cliente}/direcciones", response_model=list[DireccionResponseSchema])
async def obtener_direcciones(id_cliente: int, db: Session = Depends(get_db)):
    """Obtiene todas las direcciones de un cliente"""
    return SistemaServices.obtener_direcciones_cliente(db, id_cliente)


@router.get("/productos", response_model=list[ProductoResponseSchema])
async def obtener_productos(db: Session = Depends(get_db)):
    """Obtiene todos los productos activos"""
    return SistemaServices.obtener_productos(db)


@router.get("/productos/{id_producto}", response_model=ProductoResponseSchema)
async def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    """Obtiene un producto por ID"""
    return SistemaServices.obtener_producto(db, id_producto)


@router.post("/productos", response_model=ProductoResponseSchema)
async def crear_producto(data: ProductoCreateSchema, db: Session = Depends(get_db)):
    """Crea un nuevo producto"""
    return SistemaServices.crear_producto(db, data)


@router.put("/productos/{id_producto}", response_model=ProductoResponseSchema)
async def actualizar_producto(id_producto: int, data: ProductoUpdateSchema, db: Session = Depends(get_db)):
    """Actualiza un producto existente"""
    return SistemaServices.actualizar_producto(db, id_producto, data)


@router.get("/categorias", response_model=list[CategoriaResponseSchema])
async def obtener_categorias(db: Session = Depends(get_db)):
    """Obtiene todas las categorías"""
    return SistemaServices.obtener_categorias(db)


@router.post("/carrito/agregar", response_model=CarritoResponseSchema)
async def agregar_al_carrito(data: CarritoAgregarSchema, db: Session = Depends(get_db)):
    """Agrega un producto al carrito"""
    return SistemaServices.agregar_al_carrito(db, data)


@router.get("/carrito/{id_cliente}", response_model=CarritoResponseSchema)
async def obtener_carrito(id_cliente: int, db: Session = Depends(get_db)):
    """Obtiene el carrito de un cliente"""
    return SistemaServices.obtener_carrito(db, id_cliente)


@router.delete("/carrito/item/{id_item}")
async def eliminar_item_carrito(id_item: int, db: Session = Depends(get_db)):
    """Elimina un item del carrito"""
    return SistemaServices.eliminar_item_carrito(db, id_item)


@router.post("/pedidos/crear", response_model=PedidoResponseSchema)
async def crear_pedido(data: PedidoCreateSchema, db: Session = Depends(get_db)):
    """Crea un pedido a partir del carrito del cliente"""
    return SistemaServices.crear_pedido(db, data)


@router.get("/pedidos/{id_pedido}", response_model=PedidoResponseSchema)
async def obtener_pedido(id_pedido: int, db: Session = Depends(get_db)):
    """Obtiene un pedido por ID"""
    return SistemaServices.obtener_pedido(db, id_pedido)

@router.post("/pedidos/{id_pedido}/pagar")
async def procesar_pago(id_pedido: int, data: PagoRequestSchema, db: Session = Depends(get_db)):
    """
    Procesa el pago de un pedido.
    Envía solicitud al banco y actualiza el estado según la respuesta.
    """
    return await SistemaServices.procesar_pago(
        db,
        id_pedido,
        data.numero_tarjeta_origen,
        data.nombre_cliente,
        data.mes_exp,
        data.anio_exp,
        data.cvv
    )


class ActualizarEstadoEnvioSchema(BaseModel):
    id_pedido: int
    nuevo_estado: str 


@router.post("/envios/actualizar-estado")
async def actualizar_estado_envio(data: ActualizarEstadoEnvioSchema, db: Session = Depends(get_db)):
    """
    Webhook para que el sistema de envíos actualice el estado de un pedido.
    """
    return SistemaServices.actualizar_estado_envio(db, data.id_pedido, data.nuevo_estado)

@router.get("/catalogo")
async def obtener_catalogo(db: Session = Depends(get_db)):
    """
    📋 Endpoint principal del catálogo
    
    Devuelve el catálogo completo con:
    - Todas las categorías
    - Productos por categoría
    - Disponibilidad de cada producto
    - Stock y precios actualizados
    
    Este endpoint es para que otros sistemas consulten el catálogo
    """
    return SistemaServices.obtener_catalogo_completo(db)


@router.get("/catalogo/disponibilidad/{id_producto}")
async def consultar_disponibilidad_producto(id_producto: int, db: Session = Depends(get_db)):
    """
    🔍 Consulta la disponibilidad de UN producto específico
    
    Devuelve:
    - Stock actual
    - Estado de disponibilidad
    - Si se puede ordenar o no
    """
    return SistemaServices.consultar_disponibilidad(db, id_producto)


@router.post("/catalogo/disponibilidad/multiple")
async def consultar_disponibilidad_productos(
    data: ConsultaDisponibilidadSchema, 
    db: Session = Depends(get_db)
):
    """
    🔍 Consulta la disponibilidad de MÚLTIPLES productos a la vez
    
    Body ejemplo:
    {
        "ids_productos": [1, 2, 3, 4, 5]
    }
    
    Útil cuando otro sistema quiere verificar varios productos antes de hacer pedidos
    """
    return SistemaServices.consultar_disponibilidad_multiple(db, data.ids_productos)


@router.get("/clientes", response_model=list[ClienteResponseSchema])
async def obtener_todos_clientes(db: Session = Depends(get_db)):
    """
    👥 Obtiene todos los clientes registrados
    
    Para consultas administrativas o integración con otros sistemas
    """
    return SistemaServices.obtener_todos_clientes(db)