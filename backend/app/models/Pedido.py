from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class Pedido(Base):
    __tablename__ = "Pedido"
    
    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("Cliente.id_cliente"), nullable=False)
    id_direccion = Column(Integer, ForeignKey("Direccion.id_direccion"), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)
    estado = Column(String(30), default="PENDIENTE") 
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    cliente = relationship("Cliente", back_populates="pedidos")
    direccion = relationship("Direccion")
    items = relationship("Pedido_Item", back_populates="pedido", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="pedido")


class Pedido_Item(Base):
    __tablename__ = "Pedido_Item"
    
    id_pedido_item = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("Pedido.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("Producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(DECIMAL(10, 2), nullable=False)
    
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")

class PedidoCreateSchema(BaseModel):
    id_cliente: int
    id_direccion: int

class PedidoItemResponseSchema(BaseModel):
    id_pedido_item: int
    id_producto: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float

class PedidoResponseSchema(BaseModel):
    id_pedido: int
    id_cliente: int
    id_direccion: int
    total: float
    estado: str
    fecha_creacion: datetime
    items: List[PedidoItemResponseSchema]
    
    class Config:
        from_attributes = True

class PagoRequestSchema(BaseModel):
    numero_tarjeta_origen: str
    nombre_cliente: str
    mes_exp: int
    anio_exp: int
    cvv: str