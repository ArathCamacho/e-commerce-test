from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Pedido(Base):
    __tablename__ = "pedido"
    
    id_pedido = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_direccion = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(30), default="PENDIENTE")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    direccion = relationship("Direccion", back_populates="pedidos")
    items = relationship("Pedido_Item", back_populates="pedido", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="pedido")

class Pedido_Item(Base):
    __tablename__ = "pedido_item"
    
    id_pedido_item = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="items_pedido")

# Schemas de Pydantic
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

class PagoRequestSchema(BaseModel):
    numero_tarjeta_origen: str
    nombre_cliente: str
    mes_exp: int
    anio_exp: int
    cvv: str