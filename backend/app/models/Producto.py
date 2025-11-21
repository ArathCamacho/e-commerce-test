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
    
    # CAMPOS PARA API DISTRIBUIDA
    store_id = Column(Integer, default=1)
    talla = Column(String(20))
    color = Column(String(50))
    duracion_minutos = Column(Integer)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    items_carrito = relationship("CarritoItem", back_populates="producto")  # ✅ CORREGIDO
    items_pedido = relationship("PedidoItem", back_populates="producto")    # ✅ CORREGIDO


# Schemas de Pydantic
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
    talla: Optional[str] = None
    color: Optional[str] = None
    duracion_minutos: Optional[int] = None

class ProductoUpdateSchema(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    id_categoria: Optional[int] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    duracion_minutos: Optional[int] = None

class ProductoCatalogoAPISchema(BaseModel):
    store_id: int
    id: int
    nombre: str
    description: Optional[str] = None
    precio: float
    talla: Optional[str] = None
    color: Optional[str] = None
    stock: int
    duracion_minutos: Optional[int] = None

    class Config:
        from_attributes = True

class SolicitudCatalogoSchema(BaseModel):
    store_id: int
    category: Optional[int] = None