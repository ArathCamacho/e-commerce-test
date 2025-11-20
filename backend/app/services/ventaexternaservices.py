import json
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.VentaExterna import (
    VentaExterna,
    VentaExternaRegistroSchema,
    VentaExternaResponseSchema
)
from app.models.Producto import Producto
from app.models.Pedido import Pedido, Pedido_Item
from app.models.Cliente import Cliente


class VentaExternaServices:
    
    @staticmethod
    def registrar_venta(db: Session, datos: VentaExternaRegistroSchema):
        """
        🛍️ REGISTRAR VENTA EXTERNA
        
        Flujo:
        1. Verificar que la orden no esté duplicada
        2. Validar que el producto exista
        3. Crear cliente genérico si no existe
        4. Crear pedido con el item
        5. Descontar stock
        6. Guardar registro de venta externa
        """
        
        # 1. Verificar duplicados
        venta_existe = db.query(VentaExterna).filter(
            VentaExterna.order_id == datos.order_id
        ).first()
        
        if venta_existe:
            raise HTTPException(
                status_code=400,
                detail=f"La orden {datos.order_id} ya fue registrada anteriormente"
            )
        
        # 2. Validar que el producto exista
        producto = db.query(Producto).filter(
            Producto.id_producto == datos.product_external_id,
            Producto.store_id == datos.store_id,
            Producto.activo == True
        ).first()
        
        if not producto:
            # Guardar como ERROR si el producto no existe
            venta = VentaExterna(
                id_externo=datos.id,
                order_id=datos.order_id,
                store_id=datos.store_id,
                product_external_id=datos.product_external_id,
                product_name=datos.product_name,
                price=Decimal(str(datos.price)),
                quantity=datos.quantity,
                size=datos.size,
                color=datos.color,
                options=datos.options,
                created_at=datetime.fromisoformat(datos.created_at.replace('Z', '')),
                payment_status=datos.payment_status,
                procesado="ERROR",
                request_json=json.dumps(datos.model_dump())
            )
            db.add(venta)
            db.commit()
            db.refresh(venta)
            
            raise HTTPException(
                status_code=404,
                detail=f"Producto {datos.product_external_id} no encontrado en store {datos.store_id}"
            )
        
        # 3. Verificar stock suficiente
        if producto.stock < datos.quantity:
            venta = VentaExterna(
                id_externo=datos.id,
                order_id=datos.order_id,
                store_id=datos.store_id,
                product_external_id=datos.product_external_id,
                product_name=datos.product_name,
                price=Decimal(str(datos.price)),
                quantity=datos.quantity,
                size=datos.size,
                color=datos.color,
                options=datos.options,
                created_at=datetime.fromisoformat(datos.created_at.replace('Z', '')),
                payment_status=datos.payment_status,
                procesado="ERROR",
                request_json=json.dumps(datos.model_dump())
            )
            db.add(venta)
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {producto.stock}, Solicitado: {datos.quantity}"
            )
        
        try:
            # 4. Buscar o crear cliente genérico para ventas externas
            cliente_externo = db.query(Cliente).filter(
                Cliente.correo == "ventas.externas@sistema.com"
            ).first()
            
            if not cliente_externo:
                cliente_externo = Cliente(
                    nombre="Cliente",
                    apellido="Externo",
                    correo="ventas.externas@sistema.com",
                    telefono="0000000000",
                    contrasena="N/A"
                )
                db.add(cliente_externo)
                db.commit()
                db.refresh(cliente_externo)
            
            # 5. Crear pedido
            total = Decimal(str(datos.price)) * datos.quantity
            
            pedido = Pedido(
                id_cliente=cliente_externo.id_cliente,
                id_direccion=1,  # Dirección por defecto o NULL si es permitido
                total=total,
                estado="PAGADO" if datos.payment_status == "PAID" else "PENDIENTE",
                fecha_creacion=datetime.fromisoformat(datos.created_at.replace('Z', ''))
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            
            # 6. Crear item del pedido
            item = Pedido_Item(
                id_pedido=pedido.id_pedido,
                id_producto=producto.id_producto,
                cantidad=datos.quantity,
                precio_unitario=Decimal(str(datos.price))
            )
            db.add(item)
            
            # 7. Descontar stock
            producto.stock -= datos.quantity
            
            # 8. Crear registro de venta externa
            venta = VentaExterna(
                id_externo=datos.id,
                order_id=datos.order_id,
                store_id=datos.store_id,
                product_external_id=datos.product_external_id,
                product_name=datos.product_name,
                price=Decimal(str(datos.price)),
                quantity=datos.quantity,
                size=datos.size,
                color=datos.color,
                options=datos.options,
                created_at=datetime.fromisoformat(datos.created_at.replace('Z', '')),
                payment_status=datos.payment_status,
                procesado="PROCESADO",
                id_pedido_generado=pedido.id_pedido,
                request_json=json.dumps(datos.model_dump())
            )
            db.add(venta)
            
            db.commit()
            db.refresh(venta)
            
            return VentaExternaResponseSchema.model_validate(venta)
            
        except Exception as e:
            db.rollback()
            
            # Guardar como ERROR
            venta = VentaExterna(
                id_externo=datos.id,
                order_id=datos.order_id,
                store_id=datos.store_id,
                product_external_id=datos.product_external_id,
                product_name=datos.product_name,
                price=Decimal(str(datos.price)),
                quantity=datos.quantity,
                size=datos.size,
                color=datos.color,
                options=datos.options,
                created_at=datetime.fromisoformat(datos.created_at.replace('Z', '')),
                payment_status=datos.payment_status,
                procesado="ERROR",
                request_json=json.dumps(datos.model_dump())
            )
            db.add(venta)
            db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar venta: {str(e)}"
            )
    
    
    @staticmethod
    def consultar_ventas_externas(db: Session, order_id: str = None):
        """🔍 Consultar ventas externas registradas"""
        if order_id:
            ventas = db.query(VentaExterna).filter(
                VentaExterna.order_id == order_id
            ).all()
        else:
            ventas = db.query(VentaExterna).order_by(
                VentaExterna.fecha_registro.desc()
            ).limit(50).all()
        
        return [VentaExternaResponseSchema.model_validate(v) for v in ventas]