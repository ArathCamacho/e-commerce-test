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
    id_producto: int
    nombre: str
    cantidad: int
    precio: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_producto": 8,
                "nombre": "Playera Negra",
                "cantidad": 2,
                "precio": 199.99
            }
        }


class DatosClienteEnvioSchema(BaseModel):
    """Datos del cliente para el envío"""
    nombre: str
    telefono: str
    email: str
    direccion_completa: str
    ciudad: str
    estado: str
    codigo_postal: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "telefono": "6621234567",
                "email": "juan@example.com",
                "direccion_completa": "Calle Ejemplo 123, Col. Centro",
                "ciudad": "Hermosillo",
                "estado": "Sonora",
                "codigo_postal": "83000"
            }
        }


class EnvioSolicitudSchema(BaseModel):
    """Lo que envías a la API de envíos (CON WEBHOOK)"""
    id_orden_externa: str
    id_orden_original: int
    servicio_origen: str = "ecommerce"
    webhook_url: str  # ← NUEVO: Tu URL para recibir actualizaciones
    datos_cliente: DatosClienteEnvioSchema
    productos: List[ProductoEnvioSchema]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_orden_externa": "ECM-2024-00001",
                "id_orden_original": 15,
                "servicio_origen": "ecommerce",
                "webhook_url": "https://e-commerce-test-mm6o.onrender.com/api/envios/webhook",
                "datos_cliente": {
                    "nombre": "Juan Pérez",
                    "telefono": "6621234567",
                    "email": "juan@example.com",
                    "direccion_completa": "Calle Ejemplo 123",
                    "ciudad": "Hermosillo",
                    "estado": "Sonora",
                    "codigo_postal": "83000"
                },
                "productos": [
                    {
                        "id_producto": 8,
                        "nombre": "Playera",
                        "cantidad": 2,
                        "precio": 199.99
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