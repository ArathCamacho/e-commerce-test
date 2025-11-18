from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional

class Producto(Base):
    __tablename__ = "producto"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    imagen_url = Column(String(500))
    activo = Column(Boolean, default=True)
    
    # Relación con Categoria (OTRO LADO)
    categoria = relationship("Categoria", back_populates="productos")
    
    # Relación con otros modelos
    items_carrito = relationship("Carrito_Item", back_populates="producto")
    items_pedido = relationship("Pedido_Item", back_populates="producto")

class ProductoResponseSchema(BaseModel):
    id_producto: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    id_categoria: int
    imagen_url: Optional[str] = None
    activo: bool = True

    class Config:
        from_attributes = True

class ProductoCreateSchema(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    id_categoria: int
    imagen_url: Optional[str] = None

class ProductoUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    id_categoria: Optional[int] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None