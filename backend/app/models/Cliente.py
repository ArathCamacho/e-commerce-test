from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Cliente(Base):
    __tablename__ = "cliente"
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    apellido = Column(String(150), nullable=False)
    correo = Column(String(200), nullable=False, unique=True, index=True)
    telefono = Column(String(20))
    contrasena = Column(String(300), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    direcciones = relationship("Direccion", back_populates="cliente")
    carritos = relationship("Carrito", back_populates="cliente")
    pedidos = relationship("Pedido", back_populates="cliente")

# Schemas de Pydantic
class ClienteResponseSchema(BaseModel):
    id_cliente: int
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str] = None
    fecha_registro: datetime

    class Config:
        from_attributes = True

class ClienteRegistroSchema(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: Optional[str] = None
    contrasena: str

class ClienteLoginSchema(BaseModel):
    correo: EmailStr
    contrasena: str