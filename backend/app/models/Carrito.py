from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
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
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="carritos")
    items = relationship("CarritoItem", back_populates="carrito", cascade="all, delete-orphan")  # ✅ CORREGIDO


class CarritoItem(Base):  # ✅ RENOMBRADO (sin guion bajo)
    __tablename__ = "carrito_item"  # ← Tabla en BD sigue igual
    
    id_item = Column(Integer, primary_key=True, index=True)
    id_carrito = Column(Integer, ForeignKey("carrito.id_carrito"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto", back_populates="items_carrito")


# Schemas de Pydantic
class CarritoAgregarSchema(BaseModel):
    id_cliente: int
    id_producto: int
    cantidad: int

class CarritoItemResponseSchema(BaseModel):
    id_item: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float

class CarritoResponseSchema(BaseModel):
    id_carrito: int
    id_cliente: int
    items: List[CarritoItemResponseSchema]
    total: float