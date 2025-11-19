from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional

class Direccion(Base):
    __tablename__ = "direccion"
    
    id_direccion = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    calle = Column(String(200), nullable=False)
    ciudad = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    codigo_postal = Column(String(10), nullable=False)
    referencias = Column(String(300))
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="direcciones")
    pedidos = relationship("Pedido", back_populates="direccion")

# Schemas de Pydantic
class DireccionResponseSchema(BaseModel):
    id_direccion: int
    id_cliente: int
    calle: str
    ciudad: str
    estado: str
    codigo_postal: str
    referencias: Optional[str] = None

    class Config:
        from_attributes = True

class DireccionCreateSchema(BaseModel):
    calle: str
    ciudad: str
    estado: str
    codigo_postal: str
    #referencias: Optional[str] = None
    #ggg
