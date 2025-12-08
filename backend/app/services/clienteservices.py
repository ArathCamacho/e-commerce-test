import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from decimal import Decimal
from datetime import datetime

from app.models.Cliente import Cliente, ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema, ClienteUpdateSchema
from app.models.Direccion import Direccion, DireccionCreateSchema, DireccionResponseSchema
from app.models.Carrito import Carrito, CarritoItem, CarritoAgregarSchema, CarritoResponseSchema, CarritoItemResponseSchema
from app.models.Pedido import Pedido, PedidoItem, PedidoCreateSchema, PedidoResponseSchema, PedidoItemResponseSchema
from app.models.Producto import Producto
from app.models.Pedido import (
    Pedido,
    DireccionEnPedidoSchema,
    PedidoDetalleResponseSchema,
    ClienteEnPedidoSchema
)

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ClienteServices:

    @staticmethod
    def registrar_cliente(db: Session, datos: ClienteRegistroSchema) -> ClienteResponseSchema:
        # Verificar si el correo ya existe
        cliente_existe = db.query(Cliente).filter(Cliente.correo == datos.correo).first()
        if cliente_existe:
            raise HTTPException(
                status_code=400,
                detail="El correo ya está registrado"
            )

        # Hashear contraseña
        contrasena_hash = pwd_context.hash(datos.contrasena)

        # Crear cliente
        cliente = Cliente(
            nombre=datos.nombre,
            apellido=datos.apellido,
            correo=datos.correo,
            telefono=datos.telefono,
            contrasena=contrasena_hash
        )

        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        logger.info(f"Cliente registrado: {cliente.id_cliente} - {cliente.correo}")

        return ClienteResponseSchema.model_validate(cliente)


    @staticmethod
    def login_cliente(db: Session, datos: ClienteLoginSchema) -> ClienteResponseSchema:
        # Buscar cliente por correo
        cliente = db.query(Cliente).filter(Cliente.correo == datos.correo).first()

        if not cliente:
            raise HTTPException(
                status_code=401,
                detail="Correo o contraseña incorrectos"
            )

        # Verificar contraseña
        if not pwd_context.verify(datos.contrasena, cliente.contrasena):
            raise HTTPException(
                status_code=401,
                detail="Correo o contraseña incorrectos"
            )

        logger.info(f"Login exitoso: {cliente.id_cliente} - {cliente.correo}")

        return ClienteResponseSchema.model_validate(cliente)


    @staticmethod
    def obtener_cliente(db: Session, id_cliente: int) -> ClienteResponseSchema:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()

        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return ClienteResponseSchema.model_validate(cliente)

    @staticmethod
    def actualizar_cliente(db: Session, id_cliente: int, datos: ClienteUpdateSchema) -> ClienteResponseSchema:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        if datos.correo != cliente.correo:
            correo_existente = db.query(Cliente).filter(
                Cliente.correo == datos.correo,
                Cliente.id_cliente != id_cliente
            ).first()
            if correo_existente:
                raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

        cliente.nombre = datos.nombre
        cliente.apellido = datos.apellido
        cliente.correo = datos.correo
        cliente.telefono = datos.telefono

        db.commit()
        db.refresh(cliente)

        return ClienteResponseSchema.model_validate(cliente)

class DireccionServices:

    @staticmethod
    def agregar_direccion(db: Session, id_cliente: int, datos: DireccionCreateSchema) -> DireccionResponseSchema:
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        direccion = Direccion(
            id_cliente=id_cliente,
            calle=datos.calle,
            ciudad=datos.ciudad,
            estado=datos.estado,
            codigo_postal=datos.codigo_postal,
            referencias=datos.referencias
        )

        db.add(direccion)
        db.commit()
        db.refresh(direccion)

        logger.info(f"Dirección creada: {direccion.id_direccion} para cliente {id_cliente}")

        return DireccionResponseSchema.model_validate(direccion)


    @staticmethod
    def obtener_direcciones(db: Session, id_cliente: int):
        direcciones = db.query(Direccion).filter(Direccion.id_cliente == id_cliente).all()

        return [DireccionResponseSchema.model_validate(d) for d in direcciones]
class CarritoServices:

    @staticmethod
    def obtener_o_crear_carrito(db: Session, id_cliente: int):
        """Obtiene el carrito activo o crea uno nuevo usando consulta SQL directa"""
        from sqlalchemy import text

        # Buscar carrito existente
        query = text("SELECT id_carrito FROM carrito WHERE id_cliente = :id_cliente")
        result = db.execute(query, {"id_cliente": id_cliente}).fetchone()

        if result:
            # Devolver un objeto simple con el id_carrito
            class SimpleCarrito:
                def __init__(self, id_carrito):
                    self.id_carrito = id_carrito
                    self.id_cliente = id_cliente
            return SimpleCarrito(result.id_carrito)
        else:
            # Crear nuevo carrito
            insert_query = text("INSERT INTO carrito (id_cliente) VALUES (:id_cliente) RETURNING id_carrito")
            result = db.execute(insert_query, {"id_cliente": id_cliente})
            db.commit()

            new_id = result.fetchone().id_carrito
            logger.info(f"Carrito creado: {new_id} para cliente {id_cliente}")

            class SimpleCarrito:
                def __init__(self, id_carrito):
                    self.id_carrito = id_carrito
                    self.id_cliente = id_cliente
            return SimpleCarrito(new_id)
    @staticmethod
    def obtener_carrito(db: Session, id_cliente: int) -> CarritoResponseSchema:
        """Obtiene el carrito del cliente con todos sus items usando consulta SQL directa"""
        carrito = CarritoServices.obtener_o_crear_carrito(db, id_cliente)

        # Consulta SQL directa para obtener items del carrito con información del producto
        from sqlalchemy import text

        query = text("""
            SELECT
                ci.id_item, ci.id_producto, ci.cantidad, ci.precio_unitario,
                ci.color, ci.talla,
                p.nombre as nombre_producto, p.imagen_url as imagen
            FROM carrito_item ci
            JOIN producto p ON ci.id_producto = p.id_producto
            WHERE ci.id_carrito = :id_carrito
        """)

        result = db.execute(query, {"id_carrito": carrito.id_carrito}).fetchall()

        # Construir respuesta con items
        items_response = []
        total = Decimal('0.00')

        for item in result:
            subtotal = item.precio_unitario * item.cantidad
            total += subtotal

            items_response.append(CarritoItemResponseSchema(
                id_item=item.id_item,
                id_producto=item.id_producto,
                nombre_producto=item.nombre_producto,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario),
                subtotal=float(subtotal),
                color=item.color,
                talla=item.talla,
                imagen=item.imagen
            ))

        return CarritoResponseSchema(
            id_carrito=carrito.id_carrito,
            id_cliente=carrito.id_cliente,
            items=items_response,
            total=float(total)
        )
    @staticmethod
    def agregar_al_carrito(db: Session, datos: CarritoAgregarSchema) -> CarritoResponseSchema:
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id_cliente == datos.id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Verificar que el producto existe y está activo
        producto = db.query(Producto).filter(
            Producto.id_producto == datos.id_producto,
            Producto.activo == True
        ).first()

        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        if producto.stock < datos.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {producto.stock}"
            )

        # Obtener o crear carrito
        carrito = CarritoServices.obtener_o_crear_carrito(db, datos.id_cliente)

        # Verificar si el producto ya está en el carrito
        item_existente = db.query(CarritoItem).filter(
            CarritoItem.id_carrito == carrito.id_carrito,
            CarritoItem.id_producto == datos.id_producto,
            CarritoItem.color == datos.color,
            CarritoItem.talla == datos.talla
        ).first()

        if item_existente:
            # Actualizar cantidad
            item_existente.cantidad += datos.cantidad
        else:
            # Crear nuevo item
            nuevo_item = CarritoItem(
                id_carrito=carrito.id_carrito,
                id_producto=datos.id_producto,
                cantidad=datos.cantidad,
                precio_unitario=producto.precio,
                color=datos.color,
                talla=datos.talla
            )
            db.add(nuevo_item)

        db.commit()

        logger.info(f"Producto {datos.id_producto} agregado al carrito {carrito.id_carrito}")

        return CarritoServices.obtener_carrito(db, datos.id_cliente)


    @staticmethod
    def eliminar_item(db: Session, id_item: int, id_cliente: int):
        # Verificar que el item existe y pertenece al cliente usando consulta SQL directa
        from sqlalchemy import text

        query = text("""
            SELECT ci.id_item
            FROM carrito_item ci
            JOIN carrito c ON ci.id_carrito = c.id_carrito
            WHERE ci.id_item = :id_item AND c.id_cliente = :id_cliente
        """)

        result = db.execute(query, {"id_item": id_item, "id_cliente": id_cliente}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")

        # Eliminar el item
        item = db.query(CarritoItem).filter(CarritoItem.id_item == id_item).first()
        db.delete(item)
        db.commit()

        logger.info(f"Item {id_item} eliminado del carrito")

        return {"message": "Producto eliminado del carrito"}


    @staticmethod
    def vaciar_carrito(db: Session, id_cliente: int):
        carrito = db.query(Carrito).filter(Carrito.id_cliente == id_cliente).first()

        if not carrito:
            return {"message": "Carrito vacío"}

        # Eliminar todos los items
        db.query(CarritoItem).filter(CarritoItem.id_carrito == carrito.id_carrito).delete()
        db.commit()

        logger.info(f"Carrito vaciado: cliente {id_cliente}")

        return {"message": "Carrito vaciado"}

class PedidoServices:

    @staticmethod
    def crear_pedido_desde_carrito(db: Session, id_cliente: int, id_direccion: int) -> PedidoResponseSchema:
        from sqlalchemy import text

        # Verificar cliente
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Verificar dirección
        direccion = db.query(Direccion).filter(
            Direccion.id_direccion == id_direccion,
            Direccion.id_cliente == id_cliente
        ).first()

        if not direccion:
            raise HTTPException(
                status_code=404,
                detail="Dirección no encontrada o no pertenece al cliente"
            )

        # Obtener items del carrito con información del producto usando consulta SQL directa
        query = text("""
            SELECT
                ci.id_item, ci.id_producto, ci.cantidad, ci.precio_unitario,
                p.nombre as nombre_producto, p.stock, p.activo, p.precio as precio_actual
            FROM carrito_item ci
            JOIN carrito c ON ci.id_carrito = c.id_carrito
            JOIN producto p ON ci.id_producto = p.id_producto
            WHERE c.id_cliente = :id_cliente
        """)

        carrito_items = db.execute(query, {"id_cliente": id_cliente}).fetchall()

        if not carrito_items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")

        # Calcular total y verificar stock
        total = Decimal('0.00')
        for item in carrito_items:
            if not item.activo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El producto '{item.nombre_producto}' ya no está disponible"
                )

            if item.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{item.nombre_producto}'. Disponible: {item.stock}"
                )

            total += item.precio_unitario * item.cantidad

        # Crear pedido
        pedido = Pedido(
            id_cliente=id_cliente,
            id_direccion=id_direccion,
            total=total,
            estado="PENDIENTE"
        )

        db.add(pedido)
        db.commit()
        db.refresh(pedido)

        # Crear items del pedido y reducir stock
        for item in carrito_items:
            pedido_item = PedidoItem(
                id_pedido=pedido.id_pedido,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            db.add(pedido_item)

            # Reducir stock usando consulta SQL directa
            update_stock_query = text("""
                UPDATE producto
                SET stock = stock - :cantidad
                WHERE id_producto = :id_producto
            """)
            db.execute(update_stock_query, {
                "cantidad": item.cantidad,
                "id_producto": item.id_producto
            })

        # Vaciar carrito usando consulta SQL directa
        delete_cart_query = text("""
            DELETE FROM carrito_item
            WHERE id_carrito = (
                SELECT id_carrito FROM carrito WHERE id_cliente = :id_cliente
            )
        """)
        db.execute(delete_cart_query, {"id_cliente": id_cliente})

        db.commit()

        logger.info(f"Pedido creado: {pedido.id_pedido} - Total: ${total}")

        return PedidoServices.obtener_pedido(db, pedido.id_pedido)


    @staticmethod
    def obtener_pedido(db: Session, id_pedido: int) -> dict:
        # Consulta SQL directa para evitar problemas con relaciones de SQLAlchemy
        from sqlalchemy import text

        # Consulta del pedido sin dirección
        query = text("""
            SELECT
                p.id_pedido, p.id_cliente, p.id_direccion, p.fecha_creacion, p.total, p.estado
            FROM pedido p
            WHERE p.id_pedido = :id_pedido
        """)

        result = db.execute(query, {"id_pedido": id_pedido}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        # Consulta de items del pedido
        items_query = text("""
            SELECT
                pi.id_pedido_item, pi.id_producto, pi.cantidad, pi.precio_unitario,
                pr.nombre as producto_nombre
            FROM pedido_item pi
            JOIN producto pr ON pi.id_producto = pr.id_producto
            WHERE pi.id_pedido = :id_pedido
        """)

        items_result = db.execute(items_query, {"id_pedido": id_pedido}).fetchall()

        items_response = []
        for item in items_result:
            items_response.append({
                'id_pedido_item': item.id_pedido_item,
                'id_producto': item.id_producto,
                'cantidad': item.cantidad,
                'precio_unitario': float(item.precio_unitario),
                'producto': {
                    'nombre': item.producto_nombre,
                    'imagen': None  # No consultar imagen por simplicidad
                }
            })

        return {
            'id_pedido': result.id_pedido,
            'id_cliente': result.id_cliente,
            'id_direccion': result.id_direccion,
            'fecha_creacion': result.fecha_creacion,
            'total': float(result.total),
            'estado': result.estado,
            'items': items_response
        }


    @staticmethod
    def listar_pedidos_cliente(db: Session, id_cliente: int):
        from sqlalchemy import text

        # Consulta SQL directa para obtener pedidos sin dirección
        query = text("""
            SELECT
                p.id_pedido, p.id_cliente, p.id_direccion, p.fecha_creacion, p.total, p.estado
            FROM pedido p
            WHERE p.id_cliente = :id_cliente
            ORDER BY p.fecha_creacion DESC
        """)

        results = db.execute(query, {"id_cliente": id_cliente}).fetchall()

        pedidos = []
        for result in results:
            # Obtener items para este pedido
            items_query = text("""
                SELECT
                    pi.id_pedido_item, pi.id_producto, pi.cantidad, pi.precio_unitario,
                    pr.nombre as producto_nombre
                FROM pedido_item pi
                JOIN producto pr ON pi.id_producto = pr.id_producto
                WHERE pi.id_pedido = :id_pedido
            """)

            items_result = db.execute(items_query, {"id_pedido": result.id_pedido}).fetchall()

            items_response = []
            for item in items_result:
                items_response.append({
                    'id_pedido_item': item.id_pedido_item,
                    'id_producto': item.id_producto,
                    'cantidad': item.cantidad,
                    'precio_unitario': float(item.precio_unitario),
                    'producto': {
                        'nombre': item.producto_nombre,
                        'imagen': None
                    }
                })

            pedidos.append({
                'id_pedido': result.id_pedido,
                'id_cliente': result.id_cliente,
                'id_direccion': result.id_direccion,
                'fecha_creacion': result.fecha_creacion,
                'total': float(result.total),
                'estado': result.estado,
                'items': items_response
            })

        return pedidos


    @staticmethod
    def actualizar_estado_pedido(db: Session, id_pedido: int, nuevo_estado: str):
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        estados_validos = ["PENDIENTE", "PAGADO", "EN_PREPARACION", "ENVIADO", "ENTREGADO", "CANCELADO"]

        if nuevo_estado not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Valores permitidos: {', '.join(estados_validos)}"
            )

        pedido.estado = nuevo_estado
        db.commit()

        logger.info(f"Pedido {id_pedido} actualizado a: {nuevo_estado}")

        return {"id_pedido": id_pedido, "nuevo_estado": nuevo_estado}
    
    @staticmethod
    def obtener_detalle_pedido(db: Session, id_pedido: int) -> PedidoDetalleResponseSchema:
        """
        Obtener detalle completo de un pedido incluyendo datos de cliente y dirección
        """
        from app.models.Cliente import Cliente
        from app.models.Direccion import Direccion
        
        # Buscar el pedido
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        
        if not pedido:
            raise HTTPException(
                status_code=404,
                detail=f"Pedido {id_pedido} no encontrado"
            )
        
        # Buscar datos del cliente
        cliente = db.query(Cliente).filter(Cliente.id_cliente == pedido.id_cliente).first()
        
        if not cliente:
            raise HTTPException(
                status_code=404,
                detail=f"Cliente {pedido.id_cliente} no encontrado"
            )
        
        # Buscar datos de la dirección
        direccion = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
        
        if not direccion:
            raise HTTPException(
                status_code=404,
                detail=f"Dirección {pedido.id_direccion} no encontrada"
            )
        
        # Construir respuesta
        return PedidoDetalleResponseSchema(
            id_pedido=pedido.id_pedido,
            total=float(pedido.total),
            estado=pedido.estado,
            fecha_creacion=pedido.fecha_creacion,
            cliente=ClienteEnPedidoSchema(
                nombre=cliente.nombre,
                apellido=cliente.apellido,
                correo=cliente.correo,
                telefono=cliente.telefono
            ),
            direccion=DireccionEnPedidoSchema(
                calle=direccion.calle,
                ciudad=direccion.ciudad,
                estado=direccion.estado,
                codigo_postal=direccion.codigo_postal,
                referencias=direccion.referencias
            )
        )

    @staticmethod
    def actualizar_direccion_pedido(db: Session, id_pedido: int, id_cliente: int,
                                   nueva_direccion: dict) -> dict:
        """
        Actualizar la dirección de envío de un pedido y sincronizar con servicio externo si existe envío
        """
        from app.models.Direccion import Direccion
        from app.models.Envio import Envio
        from app.services.ventaexternaservices import VentaExternaServices

        # Verificar que el pedido existe y pertenece al cliente
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.id_cliente != id_cliente:
            raise HTTPException(status_code=403, detail="No autorizado para modificar este pedido")

        # Solo permitir editar pedidos que no estén enviados o completados
        if pedido.estado in ['ENVIADO', 'ENTREGADO']:
            raise HTTPException(
                status_code=400,
                detail="No se puede modificar la dirección de un pedido ya enviado"
            )

        # Verificar que la nueva dirección tenga los campos requeridos
        campos_requeridos = ['calle', 'ciudad', 'estado', 'codigo_postal']
        for campo in campos_requeridos:
            if campo not in nueva_direccion or not nueva_direccion[campo]:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{campo}' es requerido"
                )

        # Verificar que existe una dirección asociada al pedido (solo para validación)
        direccion_original = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
        if not direccion_original:
            raise HTTPException(status_code=404, detail="Dirección original no encontrada")

        # NO modificar la dirección original. En su lugar, crear una NUEVA dirección
        # para este pedido específico, así no afectamos otros pedidos que usen la misma dirección
        nueva_direccion_db = Direccion(
            id_cliente=id_cliente,
            calle=nueva_direccion['calle'],
            ciudad=nueva_direccion['ciudad'],
            estado=nueva_direccion['estado'],
            codigo_postal=nueva_direccion['codigo_postal'],
            referencias=nueva_direccion.get('referencias', '')
        )

        db.add(nueva_direccion_db)
        db.flush()  # Para obtener el id_direccion de la nueva dirección

        # Asignar la nueva dirección al pedido
        pedido.id_direccion = nueva_direccion_db.id_direccion

        # Verificar si existe un envío para este pedido
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()

        # Si existe envío con código de seguimiento, también actualizar en servicio externo
        envio_actualizado_externo = False
        if envio and envio.codigo_seguimiento:
            try:
                # Formatear dirección para el servicio externo: "CALLE, CIUDAD, ESTADO, CP"
                direccion_formateada = f"{nueva_direccion['calle']}, {nueva_direccion['ciudad']}, {nueva_direccion['estado']}, {nueva_direccion['codigo_postal']}"

                # Llamar al servicio externo para actualizar la dirección
                resultado_externo = VentaExternaServices.actualizar_direccion_envio(
                    envio.codigo_seguimiento,
                    direccion_formateada
                )

                envio_actualizado_externo = True
                logger.info(f"Dirección actualizada en servicio externo para pedido {id_pedido}")

            except Exception as e:
                logger.error(f"Error actualizando dirección en servicio externo: {str(e)}")
                # No fallar la operación si el servicio externo falla, pero loggear el error
                # La dirección local ya se actualizó, así que continuamos

        # Guardar cambios en la base de datos local
        db.commit()

        logger.info(f"Dirección actualizada para pedido {id_pedido} (local y externo: {envio_actualizado_externo})")

        return {
            "message": "Dirección actualizada exitosamente",
            "direccion_actualizada": True,
            "envio_actualizado": envio_actualizado_externo
        }