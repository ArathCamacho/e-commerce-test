from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Modelo SQLAlchemy
class MetodoPago(Base):
    __tablename__ = "metodo_pago"

    id_metodo_pago = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    cardholder_name = Column(String(100), nullable=False)
    card_number = Column(String(255), nullable=False)  # Encriptado
    expiry_date = Column(String(10), nullable=False)  # MM/YY
    cvv = Column(String(10), nullable=False)  # Encriptado
    is_default = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con cliente - Comentada para evitar problemas de configuración
    # cliente = relationship("Cliente", back_populates="metodos_pago")

# Esquemas para métodos de pago
class MetodoPagoCreateSchema(BaseModel):
    cardholderName: str
    cardNumber: str
    expiryDate: str
    cvv: str
    isDefault: bool = False

class MetodoPagoUpdateSchema(BaseModel):
    cardholderName: Optional[str] = None
    cardNumber: Optional[str] = None
    expiryDate: Optional[str] = None
    cvv: Optional[str] = None
    isDefault: Optional[bool] = None

class MetodoPagoResponseSchema(BaseModel):
    id: int
    id_cliente: int
    cardholderName: str
    cardNumber: str  # Se enviará enmascarado
    expiryDate: str
    isDefault: bool
    fecha_creacion: datetime
    ultima_actualizacion: datetime

    class Config:
        from_attributes = True
