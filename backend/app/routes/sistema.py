from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.services.sistemaservices import SistemaServices
from pydantic import BaseModel
from typing import List, Optional

from app.models.Cliente import ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema
from app.models.Direccion import DireccionCreateSchema, DireccionResponseSchema
from app.models.Producto import ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema
from app.models.Categoria import CategoriaResponseSchema
from app.models.Carrito import CarritoAgregarSchema, CarritoResponseSchema
from app.models.Pedido import PedidoCreateSchema, PedidoResponseSchema, PagoRequestSchema

router = APIRouter()

class ConsultaDisponibilidadSchema(BaseModel):
    """Schema para consultar disponibilidad de múltiples productos"""
    ids_productos: List[int]

class ActualizarEstadoEnvioSchema(BaseModel):
    id_pedido: int
    nuevo_estado: str


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
    🛒 CATÁLOGO COMPLETO - ENDPOINT PRINCIPAL
    
    Devuelve TODOS los productos disponibles con:
    - ID, nombre, descripción
    - Precio
    - Stock disponible
    - Estado de disponibilidad (DISPONIBLE, ULTIMAS_UNIDADES, AGOTADO)
    - Categoría
    - Si se puede ordenar o no
    
    📌 Este es el endpoint que otros equipos deben usar para consultar tu catálogo
    
    Ejemplo de uso:
    GET /api/catalogo
    """
    return SistemaServices.obtener_catalogo_completo(db)


@router.get("/catalogo/por-categoria")
async def obtener_catalogo_por_categoria(db: Session = Depends(get_db)):
    """
    📂 CATÁLOGO ORGANIZADO POR CATEGORÍAS
    
    Devuelve todos los productos agrupados por categoría
    
    Ejemplo de uso:
    GET /api/catalogo/por-categoria
    """
    return SistemaServices.obtener_catalogo_por_categoria(db)


@router.get("/catalogo/disponibilidad/{id_producto}")
async def consultar_disponibilidad_producto(id_producto: int, db: Session = Depends(get_db)):
    """
    🔍 CONSULTAR DISPONIBILIDAD DE UN PRODUCTO
    
    Verifica si un producto específico está disponible y cuánto stock hay
    
    Ejemplo de uso:
    GET /api/catalogo/disponibilidad/5
    """
    return SistemaServices.consultar_disponibilidad(db, id_producto)


@router.post("/catalogo/disponibilidad/multiple")
async def consultar_disponibilidad_productos(
    data: ConsultaDisponibilidadSchema, 
    db: Session = Depends(get_db)
):
    """
    🔍 CONSULTAR DISPONIBILIDAD DE MÚLTIPLES PRODUCTOS
    
    Verifica la disponibilidad de varios productos a la vez
    
    Body ejemplo:
    {
        "ids_productos": [1, 2, 3, 5, 10]
    }
    
    Ejemplo de uso:
    POST /api/catalogo/disponibilidad/multiple
    """
    return SistemaServices.consultar_disponibilidad_multiple(db, data.ids_productos)


@router.get("/clientes", response_model=list[ClienteResponseSchema])
async def obtener_todos_clientes(db: Session = Depends(get_db)):
    """
    👥 LISTAR TODOS LOS CLIENTES
    
    Devuelve todos los clientes registrados en el sistema
    
    Ejemplo de uso:
    GET /api/clientes
    """
    return SistemaServices.obtener_todos_clientes(db)

@router.get("/catalogo/api")
async def obtener_catalogo_api(
    store_id: int,
    category: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    🌐 ENDPOINT PARA API DISTRIBUIDA
    
    Este endpoint es el que otros equipos van a llamar para obtener tu catálogo.
    
    Parámetros (Query Params):
    - store_id: ID de tu tienda (obligatorio)
    - category: ID de categoría (opcional)
    
    Ejemplos de uso:
    
    1. Obtener TODO el catálogo:
       GET /api/catalogo/api?store_id=1
    
    2. Obtener solo productos de una categoría:
       GET /api/catalogo/api?store_id=1&category=2
    
    Respuesta:
    {
        "store_id": 1,
        "category": 2,
        "total_productos": 5,
        "productos": [
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
            }
        ]
    }
    """
    return SistemaServices.obtener_catalogo_api(db, store_id, category)


@router.post("/catalogo/api")
async def obtener_catalogo_api_post(
    solicitud: SolicitudCatalogoSchema,
    db: Session = Depends(get_db)
):
    """
    🌐 ENDPOINT PARA API DISTRIBUIDA (Método POST)
    
    Alternativa si otros equipos prefieren enviar los datos por POST
    
    Body ejemplo:
    {
        "store_id": 1,
        "category": 2
    }
    
    Respuesta igual que el GET
    """
    return SistemaServices.obtener_catalogo_api(
        db, 
        solicitud.store_id, 
        solicitud.category
    )


# ============================================
# ENDPOINT PARA LISTAR TUS CATEGORÍAS
# (Para que otros equipos sepan qué categorías tienes)
# ============================================

@router.get("/categorias/lista")
async def listar_categorias_api(db: Session = Depends(get_db)):
    """
    📂 Lista de categorías disponibles
    
    Para que otros equipos sepan qué IDs de categoría pueden consultar
    
    Respuesta:
    {
        "total_categorias": 5,
        "categorias": [
            {"id_categoria": 1, "nombre": "Electrónica"},
            {"id_categoria": 2, "nombre": "Ropa"},
            ...
        ]
    }
    """
    categorias = db.query(Categoria).all()
    return {
        "total_categorias": len(categorias),
        "categorias": [
            {
                "id_categoria": c.id_categoria,
                "nombre": c.nombre,
                "descripcion": c.descripcion
            }
            for c in categorias
        ]
    }