
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import List

class Carrito(Base):
    __tablename__ = "carrito"
    
    id_carrito = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones - Comentadas para evitar problemas de configuración
    # cliente = relationship("Cliente", back_populates="carritos")
    # items = relationship("CarritoItem", back_populates="carrito", cascade="all, delete-orphan")


class CarritoItem(Base):  # ✅ RENOMBRADO (sin guion bajo)
    __tablename__ = "carrito_item"  # ← Tabla en BD sigue igual
    
    id_item = Column(Integer, primary_key=True, index=True)
    id_carrito = Column(Integer, ForeignKey("carrito.id_carrito"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    color = Column(String(50), nullable=True)
    talla = Column(String(20), nullable=True)
    
    # Relaciones - Comentadas para evitar problemas de configuración
    # carrito = relationship("Carrito", back_populates="items")
    # producto = relationship("Producto", back_populates="items_carrito")


# Schemas de Pydantic
class CarritoAgregarSchema(BaseModel):
    id_cliente: int
    id_producto: int
    cantidad: int
    color: str = None
    talla: str = None

class CarritoItemResponseSchema(BaseModel):
    id_item: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    color: str | None = None
    talla: str | None = None
    imagen: str | None = None  # ← Cambiado para aceptar None correctamente

class CarritoResponseSchema(BaseModel):
    id_carrito: int
    id_cliente: int
    items: List[CarritoItemResponseSchema]
    total: float