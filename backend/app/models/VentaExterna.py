from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class VentaExterna(Base):
    """
    Tabla de ventas externas
    UNA FILA = UNA ORDEN COMPLETA
    """
    __tablename__ = "venta_externa"
    
    id_venta_externa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String(100), nullable=False, unique=True, index=True)  # ← Único porque es 1 orden
    total = Column(Numeric(10, 2), nullable=False)  # ← Total de la orden completa
    created_at = Column(DateTime, nullable=False)
    payment_status = Column(String(50), nullable=False)
    
    # JSON fields
    datos_cliente_json = Column(Text, nullable=False)  # ← Datos del cliente en JSON
    productos_json = Column(Text, nullable=False)  # ← TODOS los productos en JSON
    request_json = Column(Text, nullable=True)  # ← Request completo para auditoría
    
    # IDs generados (comentados porque no existen en la BD aún)
    # id_pedido_generado = Column(Integer, nullable=True)
    # id_envio_generado = Column(Integer, nullable=True)
    
    # Metadata
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    procesado = Column(String(20), default="PENDIENTE")  # PENDIENTE, PROCESADO, ERROR


# ============================================================
# SCHEMAS
# ============================================================

class DatosClienteVentaExterna(BaseModel):
    """Datos del cliente para venta externa"""
    nombre: str
    telefono: str
    email: str
    direccion: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "telefono": "6621234567",
                "email": "juan@example.com",
                "direccion": "Calle Ejemplo 123, Col. Centro"
            }
        }


class ProductoVentaExterna(BaseModel):
    """Producto individual dentro de una venta externa"""
    external_id: int
    quantity: int
    size: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "external_id": 5,
                "quantity": 2,
                "size": "M",
                "color": "Negro"
            }
        }


class VentaExternaRegistroSchemaV2(BaseModel):
    """
    Schema para recibir ventas externas desde sistema externo
    """
    order_id: str
    store_id: int  # ← No se guarda en tabla, pero se usa para validar productos
    price: float
    products: List[ProductoVentaExterna] = Field(..., min_length=1)
    datos_cliente: DatosClienteVentaExterna
    payment_status: str
    created_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-EXT-12345",
                "store_id": 1,
                "price": 599.97,
                "products": [
                    {
                        "external_id": 1,
                        "quantity": 2,
                        "size": "M",
                        "color": "Negro"
                    },
                    {
                        "external_id": 5,
                        "quantity": 1,
                        "size": "L",
                        "color": "Blanco"
                    }
                ],
                "datos_cliente": {
                    "nombre": "Juan Pérez",
                    "telefono": "6621234567",
                    "email": "juan@example.com",
                    "direccion": "Calle Ejemplo 123, Col. Centro"
                },
                "payment_status": "PAID",
                "created_at": "2025-12-07T10:30:00"
            }
        }


class VentaExternaResponseSchema(BaseModel):
    """Response con la orden completa"""
    id_venta_externa: int
    order_id: str
    total: float
    payment_status: str
    procesado: str
    productos_count: int  # ← Cantidad de productos (calculado)
    id_pedido_generado: Optional[int]
    id_envio_generado: Optional[int]
    created_at: datetime
    fecha_registro: datetime
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_products(cls, venta: 'VentaExterna'):
        """Helper para calcular productos_count desde JSON"""
        import json
        productos = json.loads(venta.productos_json) if venta.productos_json else []
        
        return cls(
            id_venta_externa=venta.id_venta_externa,
            order_id=venta.order_id,
            total=float(venta.total),
            payment_status=venta.payment_status,
            procesado=venta.procesado,
            productos_count=len(productos),
            id_pedido_generado=venta.id_pedido_generado,
            id_envio_generado=venta.id_envio_generado,
            created_at=venta.created_at,
            fecha_registro=venta.fecha_registro
        )


class VentaExternaDetalleSchema(BaseModel):
    """Response detallado con productos expandidos"""
    id_venta_externa: int
    order_id: str
    total: float
    payment_status: str
    procesado: str
    datos_cliente: DatosClienteVentaExterna
    productos: List[ProductoVentaExterna]
    id_pedido_generado: Optional[int]
    id_envio_generado: Optional[int]
    created_at: datetime
    fecha_registro: datetime