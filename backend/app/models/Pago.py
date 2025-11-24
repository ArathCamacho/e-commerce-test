from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ============================================
# MODELOS DE BASE DE DATOS (SQLAlchemy)
# ============================================

class Pago(Base):
    """
    💳 TABLA DE PAGOS
    
    Representa el pago comercial vinculado al pedido
    """
    __tablename__ = "pago"
    
    id_pago = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=True)
    
    monto = Column(Float, nullable=False)
    moneda = Column(String(50), default="MXN")
    estado = Column(String(50), default="PENDIENTE")
    metodo = Column(String(50), default="tarjeta")
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="pagos")
    solicitud = relationship("PagoSolicitud", back_populates="pago", uselist=False)
    respuesta = relationship("PagoRespuesta", back_populates="pago", uselist=False)


class PagoSolicitud(Base):
    """
    📤 TABLA DE SOLICITUDES DE PAGO
    
    Guarda lo que TÚ envías al banco
    """
    __tablename__ = "pago_solicitud"
    
    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago"), nullable=False, unique=True)
    
    # DATOS_TRANS - Lo que envías al banco
    numero_tarjeta_origen = Column(String(20), nullable=False)
    numero_tarjeta_destino = Column(String(20), nullable=False)
    nombre_cliente = Column(String(200), nullable=False)
    mes_exp = Column(Integer, nullable=False)
    anio_exp = Column(Integer, nullable=False)
    cvv = Column(String(4), nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(50), default="MXN")
    tipo = Column(String(50), default="venta")
    
    # Metadata
    creada_utc = Column(DateTime, default=datetime.utcnow)
    request_json = Column(Text, nullable=True)
    
    # Relación
    pago = relationship("Pago", back_populates="solicitud")


class PagoRespuesta(Base):
    """
    📥 TABLA DE RESPUESTAS DE PAGO
    
    Guarda lo que EL BANCO te regresa
    """
    __tablename__ = "pago_respuesta"
    
    id_respuesta = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago"), nullable=False, unique=True)
    
    # EDO_TRANS - Lo que el banco responde
    creada_utc = Column(DateTime, nullable=True)
    id_transaccion = Column(String(100), nullable=True)
    tipo_transaccion = Column(String(50), nullable=True)
    monto_transaccion = Column(Float, nullable=True)
    numero_tarjeta = Column(String(20), nullable=True)
    nombre_estado = Column(String(50), nullable=True)
    firma = Column(String(500), nullable=True)
    mensaje = Column(String(500), nullable=True)
    
    # Metadata
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    response_json = Column(Text, nullable=True)
    
    # Relación
    pago = relationship("Pago", back_populates="respuesta")


# ============================================
# SCHEMAS DE PYDANTIC
# ============================================

class PagoIniciarSchema(BaseModel):
    """Lo que el frontend te envía para iniciar el pago"""
    numero_tarjeta_origen: str
    numero_tarjeta_destino: str
    nombre_cliente: str
    mes_exp: int
    anio_exp: int
    cvv: str
    monto: float
    moneda: str = "MXN"
    tipo: str = "venta"
    id_pedido: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "numero_tarjeta_origen": "5555555555554444",
                "numero_tarjeta_destino": "4111111111111111",
                "nombre_cliente": "Juan Pérez",
                "mes_exp": 12,
                "anio_exp": 2030,
                "cvv": "456",
                "monto": 199.99,
                "moneda": "MXN",
                "tipo": "venta",
                "id_pedido": 1
            }
        }


class BancoSolicitudSchema(BaseModel):
    """Lo que TÚ envías al banco (DATOS_TRANS)"""
    id_tarjeta_origen: str
    id_tarjeta_destino: str
    nombre: str
    mes_exp: int
    anio_exp: int
    cvv: str
    monto: float
    moneda: str = "MXN"
    tipo: str = "venta"


class BancoRespuestaSchema(BaseModel):
    """Lo que EL BANCO te regresa (EDO_TRANS)"""
    creada_utc: str
    id_transaccion: str
    tipo: str
    monto: float
    numero_tarjeta: str
    id_estado_transaccion: str
    firma: str
    mensaje: Optional[str] = None


class PagoResponseSchema(BaseModel):
    """Lo que devuelves al frontend"""
    id_pago: int
    id_pedido: Optional[int] = None
    monto: float
    moneda: str
    estado: str
    metodo: str
    fecha: datetime
    
    # Datos de la solicitud
    numero_tarjeta_origen: Optional[str] = None
    nombre_cliente: Optional[str] = None
    
    # Datos de la respuesta
    id_transaccion: Optional[str] = None
    nombre_estado: Optional[str] = None
    mensaje: Optional[str] = None
    
    class Config:
        from_attributes = True