from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
import httpx
import json
from datetime import datetime
from decimal import Decimal

from app.models.Cliente import Cliente, ClienteRegistroSchema, ClienteResponseSchema
from app.models.Direccion import Direccion, DireccionCreateSchema, DireccionResponseSchema
from app.models.Categoria import Categoria, CategoriaResponseSchema
from app.models.Producto import Producto, ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema
from app.models.Carrito import (
    Carrito,
    CarritoItem,  # ← Este es el nombre real de la clase
    CarritoAgregarSchema,
    CarritoResponseSchema,
    CarritoItemResponseSchema
)
from app.models.Pedido import Pedido, PedidoItem, PedidoCreateSchema, PedidoResponseSchema, PedidoItemResponseSchema
from app.models.Pago import Pago, PagoIniciarSchema, BancoSolicitudSchema, BancoRespuestaSchema, PagoResponseSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BANCO_API_URL = "http://localhost:5000/api/transacciones"
ENVIOS_API_URL = "http://localhost:6000/api/envios/crear"
TARJETA_DESTINO_COMERCIO = "0000 0009 8765 4321"  

class SistemaServices:

    @staticmethod
    def obtener_catalogo_completo_sin_filtros(db: Session):
        """
        🛒 CATÁLOGO COMPLETO SIN FILTROS
        
        Devuelve TODOS los productos activos de TODAS las tiendas.
        No requiere parámetros.
        
        Devuelve productos en formato:
        {
            "store_id": 1,
            "id": 5,
            "nombre": "Producto",
            "description": "...",
            "precio": 299.99,
            "talla": "M",
            "color": "Rojo",
            "stock": 10,
            "duracion_minutos": null
        }
        """
        # Query: todos los productos activos
        productos = db.query(Producto).filter(Producto.activo == True).all()
        
        # Formatear respuesta
        catalogo_productos = []
        for p in productos:
            catalogo_productos.append({
                "store_id": p.store_id,
                "id": p.id_producto,
                "nombre": p.nombre,
                "description": p.descripcion,
                "precio": float(p.precio),
                "talla": p.talla,
                "color": p.color,
                "stock": p.stock,
                "duracion_minutos": p.duracion_minutos
            })
        
        return catalogo_productos

    @staticmethod
    def verificar_disponibilidad_producto(db: Session, id_producto: int, cantidad_solicitada: int):
        """Verifica si hay stock suficiente para surtir un pedido"""
        
        # 1. Validar que la cantidad sea positiva
        if cantidad_solicitada <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        # 2. Buscar el producto en la base de datos
        producto = db.query(Producto).filter(
            Producto.id_producto == id_producto
        ).first()
        
        # 3. Si no existe el producto, error
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # 4. Si el producto está inactivo, error
        if not producto.activo:
            raise HTTPException(status_code=400, detail="Producto no disponible")
        
        # 5. Devolver solo id_producto y stock
        return {
            "id_producto": producto.id_producto,
            "stock": producto.stock
        }


    @staticmethod
    def obtener_catalogo_completo(db: Session, store_id: int = 1, category: int = None):
        """
        🛒 CATÁLOGO PARA API DISTRIBUIDA
        
        Recibe:
        - store_id: ID de tu tienda
        - category: ID de categoría (opcional)
        
        Devuelve productos en formato:
        {
            "store_id": 1,
            "id": 5,
            "nombre": "Producto",
            "description": "...",
            "precio": 299.99,
            "talla": "M",
            "color": "Rojo",
            "stock": 10,
            "duracion_minutos": null
        }
        """
        # Query base: productos activos de esta tienda
        query = db.query(Producto).filter(
            Producto.activo == True,
            Producto.store_id == store_id
        )
        
        # Si enviaron categoría específica, filtrar por ella
        if category is not None:
            query = query.filter(Producto.id_categoria == category)
        
        productos = query.all()
        
        # Formatear respuesta según el formato que esperan otros equipos
        catalogo_productos = []
        for p in productos:
            catalogo_productos.append({
                "store_id": p.store_id,
                "id": p.id_producto,
                "nombre": p.nombre,
                "description": p.descripcion,
                "precio": float(p.precio),
                "talla": p.talla,
                "color": p.color,
                "stock": p.stock,
                "duracion_minutos": p.duracion_minutos
            })
        
        return catalogo_productos