from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Pedido(Base):
    __tablename__ = "pedido"
    
    id_pedido = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_direccion = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), default="PENDIENTE")
    
    # Relaciones - Usamos consultas SQL directas para evitar problemas de configuración
    # cliente = relationship("Cliente", back_populates="pedidos")
    # direccion = relationship("Direccion", back_populates="pedidos")
    # items = relationship("PedidoItem", back_populates="pedido")
    # pagos = relationship("Pago", back_populates="pedido")
    # envios = relationship("Envio", back_populates="pedido")


class PedidoItem(Base):  # ✅ RENOMBRADO (sin guion bajo)
    __tablename__ = "pedido_item"  # ← Tabla en BD sigue igual
    
    id_pedido_item = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones - Comentadas para evitar problemas de configuración
    # pedido = relationship("Pedido", back_populates="items")
    # producto = relationship("Producto", back_populates="items_pedido")


# Schemas de Pydantic
class PedidoItemCreateSchema(BaseModel):
    id_producto: int
    cantidad: int

class PedidoItemResponseSchema(BaseModel):
    id_pedido_item: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    
    class Config:
        from_attributes = True

class PedidoCreateSchema(BaseModel):
    id_cliente: int
    id_direccion: int
    items: List[PedidoItemCreateSchema]

class PedidoResponseSchema(BaseModel):
    id_pedido: int
    id_cliente: int
    id_direccion: int
    fecha_creacion: datetime
    total: float
    estado: str
    items: List[PedidoItemResponseSchema]
    
    class Config:
        from_attributes = True

class PagoRequestSchema(BaseModel):
    """Schema para solicitar un pago"""
    id_pedido: int
    numero_tarjeta: str
    nombre_titular: str
    mes_exp: int
    anio_exp: int
    cvv: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_pedido": 1,
                "numero_tarjeta": "1234 5678 9012 3456",
                "nombre_titular": "Juan Perez",
                "mes_exp": 12,
                "anio_exp": 2027,
                "cvv": "123"
            }
        }

class ClienteEnPedidoSchema(BaseModel):
    """Datos del cliente dentro del detalle del pedido"""
    nombre: str
    apellido: str
    correo: str
    telefono: str
    
    class Config:
        from_attributes = True


class DireccionEnPedidoSchema(BaseModel):
    """Datos de dirección dentro del detalle del pedido"""
    calle: str
    ciudad: str
    estado: str
    codigo_postal: str
    referencias: Optional[str] = None
    
    class Config:
        from_attributes = True


class PedidoDetalleResponseSchema(BaseModel):
    """Detalle completo del pedido con cliente y dirección"""
    id_pedido: int
    total: float
    estado: str
    fecha_creacion: datetime
    cliente: ClienteEnPedidoSchema
    direccion: DireccionEnPedidoSchema

    class Config:
        from_attributes = True


class ActualizarDireccionPedidoSchema(BaseModel):
    """Esquema para actualizar la dirección de envío de un pedido"""
    calle: str
    ciudad: str
    estado: str
    codigo_postal: str
    referencias: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "calle": "Nueva Calle 123",
                "ciudad": "Nueva Ciudad",
                "estado": "Nuevo Estado",
                "codigo_postal": "12345",
                "referencias": "Cerca del parque"
            }
        }