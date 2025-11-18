from sqlalchemy import Column, Integer, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List

class Carrito(Base):
    __tablename__ = "Carrito"
    
    id_carrito = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("Cliente.id_cliente"), nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)
    
    cliente = relationship("Cliente", back_populates="carritos")
    items = relationship("Carrito_Item", back_populates="carrito", cascade="all, delete-orphan")


class Carrito_Item(Base):
    __tablename__ = "Carrito_Item"
    
    id_item = Column(Integer, primary_key=True, autoincrement=True)
    id_carrito = Column(Integer, ForeignKey("Carrito.id_carrito"), nullable=False)
    id_producto = Column(Integer, ForeignKey("Producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto")

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