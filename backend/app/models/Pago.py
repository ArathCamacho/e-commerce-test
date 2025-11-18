from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Pago(Base):
    __tablename__ = "Pago"
    
    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("Pedido.id_pedido"), nullable=False)
    estado = Column(String(20), nullable=False)  
    monto = Column(DECIMAL(10, 2), nullable=False)
    moneda = Column(String(10), default="MXN")
    fecha = Column(DateTime, default=datetime.utcnow)
    metodo = Column(String(20), default="TARJETA")
    
    pedido = relationship("Pedido", back_populates="pagos")
    solicitudes = relationship("Pago_Solicitud", back_populates="pago")
    respuestas = relationship("Pago_Respuesta", back_populates="pago")


class Pago_Solicitud(Base):
    __tablename__ = "Pago_Solicitud"
    
    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    id_pago = Column(Integer, ForeignKey("Pago.id_pago"), nullable=False)
    numero_tarjeta_origen = Column(String(25), nullable=False)
    numero_tarjeta_destino = Column(String(25), nullable=False)
    nombre_cliente = Column(String(150), nullable=False)
    mes_exp = Column(Integer, nullable=False)
    anio_exp = Column(Integer, nullable=False)
    cvv = Column(String(10), nullable=False)
    monto = Column(DECIMAL(10, 2), nullable=False)
    moneda = Column(String(10), default="MXN")
    tipo = Column(String(20), default="TRANSFERENCIA")
    creada_utc = Column(DateTime, default=datetime.utcnow)
    request_json = Column(Text, nullable=True)
    
    pago = relationship("Pago", back_populates="solicitudes")


class Pago_Respuesta(Base):
    __tablename__ = "Pago_Respuesta"
    
    id_respuesta = Column(Integer, primary_key=True, autoincrement=True)
    id_pago = Column(Integer, ForeignKey("Pago.id_pago"), nullable=False)
    nombre_comercio = Column(String(200), nullable=True)
    creada_utc = Column(DateTime, nullable=True)
    id_transaccion = Column(String(100), nullable=True)
    tipo_transaccion = Column(String(50), nullable=True)
    monto_transaccion = Column(DECIMAL(10, 2), nullable=True)
    moneda = Column(String(10), nullable=True)
    marca_tarjeta = Column(String(50), nullable=True)
    numero_tarjeta = Column(String(25), nullable=True)
    numero_autorizacion = Column(String(100), nullable=True)
    nombre_estado = Column(String(50), nullable=True)
    firma = Column(String(50), nullable=True)
    mensaje = Column(String(200), nullable=True)
    response_json = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    pago = relationship("Pago", back_populates="respuestas")

class PagoResponseSchema(BaseModel):
    id_pago: int
    id_pedido: int
    estado: str
    monto: float
    moneda: str
    fecha: datetime
    metodo: str
    
    class Config:
        from_attributes = True

class BancoSolicitudSchema(BaseModel):
    """Schema para enviar al banco"""
    NumeroTarjetaOrigen: str
    NumeroTarjetaDestino: str
    NombreCliente: str
    MesExp: int
    AnioExp: int
    Cvv: str
    Monto: float
    Moneda: str = "MXN"

class BancoRespuestaSchema(BaseModel):
    """Schema que responde el banco"""
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