import json
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict, Any
import logging

from app.models.VentaExterna import (
    VentaExterna,
    VentaExternaRegistroSchemaV2,
    VentaExternaResponseSchema,
    VentaExternaDetalleSchema,
    ProductoVentaExterna,
    DatosClienteVentaExterna
)
from app.models.Producto import Producto
from app.models.Pedido import Pedido, PedidoItem
from app.models.Cliente import Cliente

logger = logging.getLogger(__name__)


class VentaExternaServices:
    
    @staticmethod
    def _obtener_o_crear_cliente_externo(db: Session) -> Cliente:
        """Helper: Obtiene o crea el cliente para ventas externas"""
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
        
        return cliente_externo
    
    
    @staticmethod
    def registrar_venta_v2(
        db: Session, 
        datos: VentaExternaRegistroSchemaV2
    ) -> None:
        """
        Registrar venta externa completa (UNA FILA = UNA ORDEN)
        
        Proceso:
        1. Verificar que la orden no exista
        2. Validar todos los productos y stock
        3. Descontar stock del inventario
        4. Guardar en venta_externa (1 fila con productos en JSON)
        
        NO SE CREA PEDIDO - Solo registro y descuento de inventario
        
        No retorna nada - solo registra en BD (204 No Content)
        """
        store_id = datos.store_id
        
        # 1. VERIFICAR SI LA ORDEN YA EXISTE
        venta_existe = db.query(VentaExterna).filter(
            VentaExterna.order_id == datos.order_id
        ).first()
        
        if venta_existe:
            raise HTTPException(
                status_code=400,
                detail=f"La orden {datos.order_id} ya fue registrada anteriormente"
            )
        
        # 2. VALIDAR TODOS LOS PRODUCTOS
        productos_validados = []
        errores = []
        
        for prod_data in datos.products:
            producto = db.query(Producto).filter(
                Producto.id_producto == prod_data.external_id,
                Producto.store_id == store_id,
                Producto.activo == True
            ).first()
            
            if not producto:
                errores.append(
                    f"Producto {prod_data.external_id} no encontrado o inactivo en store {store_id}"
                )
                continue
                
            if producto.stock < prod_data.quantity:
                errores.append(
                    f"Producto '{producto.nombre}' (ID: {prod_data.external_id}): "
                    f"Stock insuficiente. Disponible: {producto.stock}, Solicitado: {prod_data.quantity}"
                )
                continue
            
            productos_validados.append({
                'producto': producto,
                'data': prod_data
            })
        
        # 3. SI HAY ERRORES, REGISTRAR Y LANZAR EXCEPCIÓN
        if errores:
            # Guardar como ERROR
            fecha_creacion = datetime.fromisoformat(datos.created_at.replace('Z', '')) if datos.created_at else datetime.utcnow()
            
            venta_error = VentaExterna(
                order_id=datos.order_id,
                total=Decimal(str(datos.price)),
                created_at=fecha_creacion,
                payment_status=datos.payment_status,
                datos_cliente_json=json.dumps(datos.datos_cliente.model_dump()),
                productos_json=json.dumps([p.model_dump() for p in datos.products]),
                request_json=json.dumps(datos.model_dump()),
                procesado="ERROR"
            )
            db.add(venta_error)
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail={"errores": errores, "orden": datos.order_id}
            )
        
        # 4. PROCESAR LA VENTA (SOLO DESCUENTO DE INVENTARIO)
        try:
            fecha_venta = datetime.fromisoformat(datos.created_at.replace('Z', '')) if datos.created_at else datetime.utcnow()
            
            # Descontar stock de cada producto
            for item_validado in productos_validados:
                producto = item_validado['producto']
                prod_data = item_validado['data']
                
                # Descontar stock
                producto.stock -= prod_data.quantity
                logger.info(f"Stock descontado: {producto.nombre} - Cantidad: {prod_data.quantity}")
            
            # Guardar venta externa (UNA SOLA FILA)
            venta = VentaExterna(
                order_id=datos.order_id,
                total=Decimal(str(datos.price)),
                created_at=fecha_venta,
                payment_status=datos.payment_status,
                datos_cliente_json=json.dumps(datos.datos_cliente.model_dump()),
                productos_json=json.dumps([p.model_dump() for p in datos.products]),
                request_json=json.dumps(datos.model_dump()),
                procesado="PROCESADO"
            )
            db.add(venta)
            
            # Commit de toda la transacción
            db.commit()
            
            logger.info(f"✅ Venta externa procesada: {datos.order_id} - Total: ${datos.price}")
            
        except HTTPException:
            raise
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error procesando venta externa: {str(e)}")
            
            # Guardar como ERROR
            try:
                fecha_creacion = datetime.fromisoformat(datos.created_at.replace('Z', '')) if datos.created_at else datetime.utcnow()
                
                venta_error = VentaExterna(
                    order_id=datos.order_id,
                    total=Decimal(str(datos.price)),
                    created_at=fecha_creacion,
                    payment_status=datos.payment_status,
                    datos_cliente_json=json.dumps(datos.datos_cliente.model_dump()),
                    productos_json=json.dumps([p.model_dump() for p in datos.products]),
                    request_json=json.dumps(datos.model_dump()),
                    procesado="ERROR"
                )
                db.add(venta_error)
                db.commit()
            except:
                pass
            
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar venta externa: {str(e)}"
            )
    
    
    @staticmethod
    def consultar_ventas_externas(
        db: Session, 
        order_id: str = None,
        procesado: str = None,
        limit: int = 50
    ) -> List[VentaExternaResponseSchema]:
        """
        Consultar ventas externas con filtros opcionales
        """
        query = db.query(VentaExterna)
        
        if order_id:
            query = query.filter(VentaExterna.order_id == order_id)
        
        if procesado:
            query = query.filter(VentaExterna.procesado == procesado)
        
        ventas = query.order_by(VentaExterna.fecha_registro.desc()).limit(limit).all()
        
        return [VentaExternaResponseSchema.from_orm_with_products(v) for v in ventas]
    
    
    @staticmethod
    def consultar_orden_completa(
        db: Session, 
        order_id: str
    ) -> VentaExternaDetalleSchema:
        """
        Consulta el detalle completo de una orden específica
        Incluye productos y datos del cliente expandidos
        """
        venta = db.query(VentaExterna).filter(
            VentaExterna.order_id == order_id
        ).first()
        
        if not venta:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró la orden {order_id}"
            )
        
        # Parsear JSON
        productos = json.loads(venta.productos_json)
        datos_cliente = json.loads(venta.datos_cliente_json)
        
        return VentaExternaDetalleSchema(
            id_venta_externa=venta.id_venta_externa,
            order_id=venta.order_id,
            total=float(venta.total),
            payment_status=venta.payment_status,
            procesado=venta.procesado,
            datos_cliente=DatosClienteVentaExterna(**datos_cliente),
            productos=[ProductoVentaExterna(**p) for p in productos],
            # id_pedido_generado=venta.id_pedido_generado,  # Comentado
            # id_envio_generado=venta.id_envio_generado,  # Comentado
            created_at=venta.created_at,
            fecha_registro=venta.fecha_registro
        )
    
    
    @staticmethod
    def obtener_stats(db: Session) -> Dict[str, Any]:
        """
        Estadísticas generales de ventas externas
        """
        from sqlalchemy import func
        
        total_ordenes = db.query(func.count(VentaExterna.id_venta_externa)).scalar()
        
        ordenes_procesadas = db.query(
            func.count(VentaExterna.id_venta_externa)
        ).filter(
            VentaExterna.procesado == "PROCESADO"
        ).scalar()
        
        ordenes_error = db.query(
            func.count(VentaExterna.id_venta_externa)
        ).filter(
            VentaExterna.procesado == "ERROR"
        ).scalar()
        
        total_vendido = db.query(
            func.sum(VentaExterna.total)
        ).filter(
            VentaExterna.procesado == "PROCESADO"
        ).scalar() or 0
        
        return {
            "total_ordenes": total_ordenes,
            "ordenes_procesadas": ordenes_procesadas,
            "ordenes_error": ordenes_error,
            "ordenes_pendientes": total_ordenes - ordenes_procesadas - ordenes_error,
            "tasa_exito": round((ordenes_procesadas / total_ordenes * 100), 2) if total_ordenes > 0 else 0,
            "total_vendido": float(total_vendido)
        }