import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from decimal import Decimal
from datetime import datetime

from app.models.Cliente import Cliente, ClienteRegistroSchema, ClienteLoginSchema, ClienteResponseSchema
from app.models.Direccion import Direccion, DireccionCreateSchema, DireccionResponseSchema
from app.models.Carrito import Carrito, CarritoItem, CarritoAgregarSchema, CarritoResponseSchema, CarritoItemResponseSchema
from app.models.Pedido import Pedido, PedidoItem, PedidoCreateSchema, PedidoResponseSchema, PedidoItemResponseSchema
from app.models.Producto import Producto

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
    def obtener_o_crear_carrito(db: Session, id_cliente: int) -> Carrito:
        """Obtiene el carrito activo o crea uno nuevo"""
        carrito = db.query(Carrito).filter(Carrito.id_cliente == id_cliente).first()
        
        if not carrito:
            carrito = Carrito(id_cliente=id_cliente)
            db.add(carrito)
            db.commit()
            db.refresh(carrito)
            logger.info(f"Carrito creado: {carrito.id_carrito} para cliente {id_cliente}")
        
        return carrito
    @staticmethod
    def obtener_carrito(db: Session, id_cliente: int) -> CarritoResponseSchema:
        """Obtiene el carrito del cliente con todos sus items"""
        carrito = CarritoServices.obtener_o_crear_carrito(db, id_cliente)
        
        # Construir respuesta con items
        items_response = []
        total = Decimal('0.00')
        
        for item in carrito.items:
            subtotal = item.precio_unitario * item.cantidad
            total += subtotal
            
            items_response.append(CarritoItemResponseSchema(
                id_item=item.id_item,
                id_producto=item.id_producto,
                nombre_producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario),
                subtotal=float(subtotal),
                color=item.color,
                talla=item.talla,
                imagen=item.producto.imagen if hasattr(item.producto, 'imagen') else None
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
        db.refresh(carrito)
        
        logger.info(f"Producto {datos.id_producto} agregado al carrito {carrito.id_carrito}")
        
        return CarritoServices.obtener_carrito(db, datos.id_cliente)
    
    
    @staticmethod
    def eliminar_item(db: Session, id_item: int, id_cliente: int):
        item = db.query(CarritoItem).filter(CarritoItem.id_item == id_item).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
        
        # Verificar que el item pertenece al cliente
        if item.carrito.id_cliente != id_cliente:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este item")
        
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
        
        # Obtener carrito
        carrito = db.query(Carrito).filter(Carrito.id_cliente == id_cliente).first()
        
        if not carrito or not carrito.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")
        
        # Calcular total y verificar stock
        total = Decimal('0.00')
        for item in carrito.items:
            producto = item.producto
            
            if not producto.activo:
                raise HTTPException(
                    status_code=400,
                    detail=f"El producto '{producto.nombre}' ya no está disponible"
                )
            
            if producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}"
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
        for item in carrito.items:
            pedido_item = PedidoItem(
                id_pedido=pedido.id_pedido,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            db.add(pedido_item)
            
            # Reducir stock
            item.producto.stock -= item.cantidad
        
        # Vaciar carrito
        db.query(CarritoItem).filter(CarritoItem.id_carrito == carrito.id_carrito).delete()
        
        db.commit()
        db.refresh(pedido)
        
        logger.info(f"Pedido creado: {pedido.id_pedido} - Total: ${total}")
        
        return PedidoServices.obtener_pedido(db, pedido.id_pedido)
    
    
    @staticmethod
    def obtener_pedido(db: Session, id_pedido: int) -> PedidoResponseSchema:
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        items_response = [
            PedidoItemResponseSchema.model_validate(item)
            for item in pedido.items
        ]
        
        return PedidoResponseSchema(
            id_pedido=pedido.id_pedido,
            id_cliente=pedido.id_cliente,
            id_direccion=pedido.id_direccion,
            fecha_creacion=pedido.fecha_creacion,
            total=float(pedido.total),
            estado=pedido.estado,
            items=items_response
        )
    
    
    @staticmethod
    def listar_pedidos_cliente(db: Session, id_cliente: int):
        pedidos = db.query(Pedido).filter(
            Pedido.id_cliente == id_cliente
        ).order_by(Pedido.fecha_creacion.desc()).all()
        
        return [PedidoServices.obtener_pedido(db, p.id_pedido) for p in pedidos]
    
    
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