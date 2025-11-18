from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel

class Categoria(Base):
    __tablename__ = "categoria"
    
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(300))
    
    # Relación con Producto
    productos = relationship("Producto", back_populates="categoria")

# Schemas de Pydantic
class CategoriaResponseSchema(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: str | None = None

    class Config:
        from_attributes = True