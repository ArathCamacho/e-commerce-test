from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ============================================
# MODELO DE BASE DE DATOS (SQLAlchemy)
# ============================================

class Envio(Base):
    """
    📦 TABLA DE ENVÍOS
    
    Guarda cada solicitud de envío y su seguimiento
    """
    __tablename__ = "envio"
    
    id_envio = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # ✅ id_pedido es OPCIONAL (nullable=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=True)
    
    # SOLICITUD - Lo que enviaste
    id_orden_externa = Column(String(100), nullable=False, unique=True)
    id_orden_original = Column(Integer, nullable=False)
    servicio_origen = Column(String(100), default="ecommerce")
    
    # RESPUESTA - Lo que recibiste
    codigo_seguimiento = Column(String(100), nullable=True)
    estado_actual = Column(String(50), nullable=True)
    ubicacion_actual = Column(String(200), nullable=True)
    fecha_actualizacion = Column(DateTime, nullable=True)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    request_json = Column(Text, nullable=True)
    response_json = Column(Text, nullable=True)
    
    # Relación
    pedido = relationship("Pedido", back_populates="envios")


# ============================================
# SCHEMAS DE PYDANTIC
# ============================================

class ProductoEnvioSchema(BaseModel):
    """Producto dentro de la solicitud de envío"""
    sku: str  # ← Cambiado de id_producto
    nombre: str
    cantidad: int
    precio_unitario: float  # ← Cambiado de precio
    
    class Config:
        json_schema_extra = {
            "example": {
                "sku": "ITEM01",
                "nombre": "Playera Negra",
                "cantidad": 2,
                "precio_unitario": 199.99
            }
        }


class DatosClienteEnvioSchema(BaseModel):
    """Datos del cliente para el envío"""
    nombre: str
    telefono: str
    email: str
    direccion: str  # ← Cambiado de direccion_completa
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "telefono": "6621234567",
                "email": "juan@example.com",
                "direccion": "Calle Ejemplo 123, Col. Centro"
            }
        }


class EnvioSolicitudSchema(BaseModel):
    """Lo que envías a la API de envíos (CON WEBHOOK)"""
    id_orden_externa: str
    id_orden_original: str  # ← Cambiado a string
    servicio_origen: str = "ecommerce"
    webhook_url: str
    datos_cliente: DatosClienteEnvioSchema
    productos: List[ProductoEnvioSchema]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_orden_externa": "003",
                "id_orden_original": "P-456",
                "servicio_origen": "Tienda Test",
                "webhook_url": "https://e-commerce-test-mm6o.onrender.com/api/envios/webhook",
                "datos_cliente": {
                    "nombre": "Ana Gomez",
                    "telefono": "5551234",
                    "email": "ana@ejemplo.com",
                    "direccion": "Calle Falsa 123"
                },
                "productos": [
                    {
                        "sku": "ITEM01",
                        "nombre": "Camiseta",
                        "cantidad": 2,
                        "precio_unitario": 20.00
                    }
                ]
            }
        }


class EnvioRespuestaSchema(BaseModel):
    """Lo que la API de envíos te devuelve"""
    id_orden_externa: str
    codigo_seguimiento: str
    estado_actual: str
    ubicacion_actual: str
    fecha_actualizacion: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_orden_externa": "ECM-2024-00001",
                "codigo_seguimiento": "ENV-ABC123",
                "estado_actual": "EN_PREPARACION",
                "ubicacion_actual": "Centro de distribución Hermosillo",
                "fecha_actualizacion": "2024-11-19T10:30:00Z"
            }
        }


class EnvioResponseSchema(BaseModel):
    """Lo que devuelves al frontend"""
    id_envio: int
    id_pedido: Optional[int] = None
    id_orden_externa: str
    codigo_seguimiento: Optional[str] = None
    estado_actual: Optional[str] = None
    ubicacion_actual: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True