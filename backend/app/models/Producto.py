from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional

class Producto(Base):
    __tablename__ = "producto"
    
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)
    id_categoria = Column(Integer, ForeignKey("Categoria.id_categoria"), nullable=False)
    imagen_url = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True)
    
    categoria = relationship("Categoria", back_populates="productos")

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

class ProductoResponseSchema(BaseModel):
    id_producto: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    stock: int
    id_categoria: int
    imagen_url: Optional[str]
    activo: bool
    
    class Config:
        from_attributes = True