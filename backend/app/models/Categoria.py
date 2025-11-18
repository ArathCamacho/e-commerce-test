from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional

class Categoria(Base):
    __tablename__ = "categoria"
    
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(300), nullable=True)
    
    productos = relationship("Producto", back_populates="categoria")

class CategoriaCreateSchema(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaResponseSchema(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str]
    
    class Config:
        from_attributes = True