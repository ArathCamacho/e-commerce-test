from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# ============================================
# MODELO DE BASE DE DATOS (SQLAlchemy)
# ============================================

class Pago(Base):
    """
    💳 TABLA DE PAGOS
    
    Guarda cada transacción con el banco
    """
    __tablename__ = "pago"
    
    id_pago = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=True)
    
    # Lo que enviaste
    numero_tarjeta_origen = Column(String(25), nullable=False)
    nombre_cliente = Column(String(150), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(10), default="MXN")
    
    # Lo que recibiste del banco
    estado = Column(String(20), default="PENDIENTE")  # PENDIENTE, APROBADO, RECHAZADO, ERROR
    creada_utc = Column(DateTime, nullable=True)
    id_transaccion = Column(String(100), nullable=True)
    tipo = Column(String(50), nullable=True)
    numero_tarjeta = Column(String(25), nullable=True)
    id_estado_transaccion = Column(Integer, nullable=True)
    firma = Column(String(100), nullable=True)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    request_json = Column(Text, nullable=True)  # Lo que enviaste (auditoría)
    response_json = Column(Text, nullable=True)  # Lo que recibiste (auditoría)
    
    # Relación
    pedido = relationship("Pedido", back_populates="pagos")


# ============================================
# SCHEMAS DE PYDANTIC
# ============================================

class PagoIniciarSchema(BaseModel):
    """Lo que recibes del frontend"""
    numero_tarjeta_origen: str
    nombre_cliente: str
    mes_exp: int
    anio_exp: int
    cvv: str
    monto: float
    moneda: str = "MXN"
    id_pedido: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero_tarjeta_origen": "1234 5678 9012 3456",
                "nombre_cliente": "Juan Perez",
                "mes_exp": 12,
                "anio_exp": 2027,
                "cvv": "123",
                "monto": 1250.50,
                "moneda": "MXN"
            }
        }


class BancoSolicitudSchema(BaseModel):
    """Lo que envías al banco"""
    numero_tarjeta_origen: str
    numero_tarjeta_destino: str
    nombre_cliente: str
    mes_exp: int
    anio_exp: int
    cvv: str
    monto: float
    moneda: str


class BancoRespuestaSchema(BaseModel):
    """Lo que el banco te devuelve"""
    creada_utc: Optional[str] = None
    id_transaccion: Optional[str] = None
    tipo: Optional[str] = None
    monto: Optional[float] = None
    numero_tarjeta: Optional[str] = None
    id_estado_transaccion: Optional[int] = None
    firma: Optional[str] = None


class PagoResponseSchema(BaseModel):
    """Lo que devuelves al frontend"""
    id_pago: int
    estado: str
    monto: float
    id_transaccion: Optional[str] = None
    firma: Optional[str] = None
    
    class Config:
        from_attributes = True