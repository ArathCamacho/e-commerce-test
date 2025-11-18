from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Cliente(Base):
    __tablename__ = "Cliente"
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    apellido = Column(String(150), nullable=False)
    correo = Column(String(200), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)
    contrasena = Column(String(300), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    direcciones = relationship("Direccion", back_populates="cliente")
    carritos = relationship("Carrito", back_populates="cliente")
    pedidos = relationship("Pedido", back_populates="cliente")

class ClienteRegistroSchema(BaseModel):
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str] = None
    contrasena: str

class ClienteLoginSchema(BaseModel):
    correo: str
    contrasena: str

class ClienteResponseSchema(BaseModel):
    id_cliente: int
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str]
    fecha_registro: datetime
    
    class Config:
        from_attributes = True