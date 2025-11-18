from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Pago(Base):
    __tablename__ = "pago"
    
    id_pago = Column(Integer, primary_key=True, index=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    estado = Column(String(20), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(10), default="MXN")
    fecha = Column(DateTime, default=datetime.utcnow)
    metodo = Column(String(20), default="TARJETA")
    
    # Relaciones
    pedido = relationship("Pedido", back_populates="pagos")
    solicitudes = relationship("Pago_Solicitud", back_populates="pago")
    respuestas = relationship("Pago_Respuesta", back_populates="pago")

class Pago_Solicitud(Base):
    __tablename__ = "pago_solicitud"
    
    id_solicitud = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago"), nullable=False)
    numero_tarjeta_origen = Column(String(25), nullable=False)
    numero_tarjeta_destino = Column(String(25), nullable=False)
    nombre_cliente = Column(String(150), nullable=False)
    mes_exp = Column(Integer, nullable=False)
    anio_exp = Column(Integer, nullable=False)
    cvv = Column(String(10), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(10), default="MXN")
    tipo = Column(String(20), default="TRANSFERENCIA")
    creada_utc = Column(DateTime, default=datetime.utcnow)
    request_json = Column(Text)
    
    # Relaciones
    pago = relationship("Pago", back_populates="solicitudes")

class Pago_Respuesta(Base):
    __tablename__ = "pago_respuesta"
    
    id_respuesta = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago"), nullable=False)
    nombre_comercio = Column(String(200))
    creada_utc = Column(DateTime)
    id_transaccion = Column(String(100))
    tipo_transaccion = Column(String(50))
    monto_transaccion = Column(Numeric(10, 2))
    moneda = Column(String(10))
    marca_tarjeta = Column(String(50))
    numero_tarjeta = Column(String(25))
    numero_autorizacion = Column(String(100))
    nombre_estado = Column(String(50))
    firma = Column(String(50))
    mensaje = Column(String(200))
    response_json = Column(Text)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    pago = relationship("Pago", back_populates="respuestas")

# Schemas de Pydantic
class BancoSolicitudSchema(BaseModel):
    NumeroTarjetaOrigen: str
    NumeroTarjetaDestino: str
    NombreCliente: str
    MesExp: int
    AnioExp: int
    Cvv: str
    Monto: float
    Moneda: str

class BancoRespuestaSchema(BaseModel):
    NombreComercio: Optional[str] = None
    CreadaUTC: Optional[str] = None
    IdTransaccion: Optional[str] = None
    TipoTransaccion: Optional[str] = None
    MontoTransaccion: Optional[float] = None
    Moneda: Optional[str] = None
    MarcaTarjeta: Optional[str] = None
    NumeroTarjeta: Optional[str] = None
    NumeroAutorizacion: Optional[str] = None
    NombreEstado: Optional[str] = None
    Firma: Optional[str] = None
    Mensaje: Optional[str] = None