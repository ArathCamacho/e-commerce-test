from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Pago(Base):

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

    __tablename__ = "pago_respuesta"
    
    id_respuesta = Column(Integer, primary_key=True, index=True)
    id_pago = Column(Integer, ForeignKey("pago.id_pago"), nullable=False, unique=True)
    
    creada_utc = Column(DateTime, nullable=True)
    id_transaccion = Column(String(100), nullable=True)
    tipo_transaccion = Column(String(50), nullable=True)
    monto_transaccion = Column(Float, nullable=True)
    numero_tarjeta = Column(String(20), nullable=True)
    nombre_estado = Column(String(50), nullable=True)
    firma = Column(String(500), nullable=True)
    mensaje = Column(String(500), nullable=True)
    
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    response_json = Column(Text, nullable=True)

    pago = relationship("Pago", back_populates="respuesta")


# ==================== SCHEMAS PYDANTIC ====================


class PagoFrontendSchema(BaseModel):
    """
    🌐 LO QUE EL FRONTEND ENVÍA
    El cliente solo proporciona los datos de SU tarjeta.
    La tarjeta destino se agrega automáticamente en el backend.
    """
    numero_tarjeta_origen: str
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
                "nombre_cliente": "Comprador 1",
                "mes_exp": 12,
                "anio_exp": 2030,
                "cvv": "111",
                "monto": 10.00,
                "moneda": "MXN",
                "tipo": "venta",
                "id_pedido": 1
            }
        }


class PagoIniciarSchema(BaseModel):
    """
    🔧 SCHEMA INTERNO COMPLETO
    Usado internamente en el backend, incluye ambas tarjetas.
    """
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
                "numero_tarjeta_destino": "4111111111111115",
                "nombre_cliente": "Arath Camacho",
                "mes_exp": 12,
                "anio_exp": 2028,
                "cvv": "111",
                "monto": 199.99,
                "moneda": "MXN",
                "tipo": "venta",
                "id_pedido": 1
            }
        }


class BancoSolicitudSchema(BaseModel):
    """
    🏦 FORMATO QUE ESPERA EL BANCO (PascalCase)
    Se usa para convertir los datos antes de enviarlos.
    """
    NumeroTarjetaOrigen: str = Field(alias="numero_tarjeta_origen")
    NumeroTarjetaDestino: str = Field(alias="numero_tarjeta_destino")
    NombreCliente: str = Field(alias="nombre_cliente")
    MesExp: int = Field(alias="mes_exp")
    AnioExp: int = Field(alias="anio_exp")
    Cvv: str = Field(alias="cvv")
    Monto: float = Field(alias="monto")
    
    class Config:
        populate_by_name = True


class BancoRespuestaSchema(BaseModel):
    """
    🏦 FORMATO QUE DEVUELVE EL BANCO (PascalCase)
    """
    CreadaUTC: str
    IdTransaccion: str
    TipoTransaccion: str
    MontoTransaccion: float
    MarcaTarjeta: Optional[str] = None
    NumeroTarjeta: str
    NumeroAutorizacion: Optional[str] = None
    NombreEstado: str
    Firma: str
    Mensaje: Optional[str] = None


class PagoResponseSchema(BaseModel):
    """
    📤 LO QUE SE DEVUELVE AL FRONTEND
    Información completa del pago procesado.
    """
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