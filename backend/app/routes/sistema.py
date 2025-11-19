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