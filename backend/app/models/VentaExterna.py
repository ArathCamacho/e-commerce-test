from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ============================================
# MODELO DE BASE DE DATOS (SQLAlchemy)
# ============================================

class VentaExterna(Base):
    """
    🛍️ REGISTRO DE VENTAS EXTERNAS
    
    Guarda las ventas que otros sistemas te notifican
    """
    __tablename__ = "venta_externa"
    
    id_venta_externa = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Datos que recibes de ellos
    id_externo = Column(Integer, nullable=True)  # Su ID interno
    order_id = Column(String(100), nullable=False, unique=True)  # Su número de orden
    store_id = Column(Integer, nullable=False)  # Tu store_id
    product_external_id = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    product_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    size = Column(String(20), nullable=True)
    color = Column(String(50), nullable=True)
    options = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    payment_status = Column(String(50), nullable=False)
    
    # Control interno
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    procesado = Column(String(20), default="PENDIENTE")  # PENDIENTE, PROCESADO, ERROR
    id_pedido_generado = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=True)
    request_json = Column(Text, nullable=True)  # JSON completo recibido
    
    # Relaciones
    producto = relationship("Producto")
    pedido = relationship("Pedido")


# ============================================
# SCHEMAS DE PYDANTIC
# ============================================

class VentaExternaRegistroSchema(BaseModel):
    """Lo que recibes del webhook"""
    id: Optional[int] = None
    order_id: str
    store_id: int
    product_external_id: int
    product_name: str
    price: float
    quantity: int
    size: Optional[str] = None
    color: Optional[str] = None
    options: Optional[str] = None
    created_at: str  # "2025-11-20T10:30:00"
    payment_status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "order_id": "ORD-EXT-12345",
                "store_id": 1,
                "product_external_id": 1,
                "product_name": "Playera Básica",
                "price": 199.99,
                "quantity": 2,
                "size": "M",
                "color": "Negro",
                "options": null,
                "created_at": "2025-11-20T10:30:00",
                "payment_status": "PAID"
            }
        }


class VentaExternaResponseSchema(BaseModel):
    """Lo que devuelves después de procesar"""
    id_venta_externa: int
    order_id: str
    product_name: str
    quantity: int
    price: float
    payment_status: str
    procesado: str
    id_pedido_generado: Optional[int]
    fecha_registro: datetime
    
    class Config:
        from_attributes = True