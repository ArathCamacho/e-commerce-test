from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
import httpx
import json
from datetime import datetime
from decimal import Decimal

from app.models.Cliente import Cliente, ClienteRegistroSchema, ClienteResponseSchema
from app.models.Direccion import Direccion, DireccionCreateSchema, DireccionResponseSchema
from app.models.Categoria import Categoria, CategoriaResponseSchema
from app.models.Producto import Producto, ProductoCreateSchema, ProductoUpdateSchema, ProductoResponseSchema
from app.models.Carrito import Carrito, Carrito_Item, CarritoAgregarSchema, CarritoResponseSchema, CarritoItemResponseSchema
from app.models.Pedido import Pedido, Pedido_Item, PedidoCreateSchema, PedidoResponseSchema, PedidoItemResponseSchema
from app.models.Pago import Pago, Pago_Solicitud, Pago_Respuesta, BancoSolicitudSchema, BancoRespuestaSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BANCO_API_URL = "http://localhost:5000/api/transacciones"
ENVIOS_API_URL = "http://localhost:6000/api/envios/crear"
TARJETA_DESTINO_COMERCIO = "0000 0009 8765 4321"  

class SistemaServices:

    @staticmethod
    def hash_password(password: str) -> str:
        """Devuelve la contraseña tal cual, sin hash"""
        if not isinstance(password, str):
            password = str(password, "utf-8") if isinstance(password, bytes) else str(password)
        password = password.strip()
        if len(password) == 0:
            raise HTTPException(status_code=400, detail="La contraseña no puede estar vacía")
        return password  # ✅ sin hash

    @staticmethod
    def verificar_password(plain_password: str, hash_password: str) -> bool:
        """Solo compara texto plano"""
        return plain_password == hash_password

    @staticmethod
    def registrar_cliente(db: Session, data: ClienteRegistroSchema) -> ClienteResponseSchema:
        """Registra un nuevo cliente sin hash en la contraseña"""
        existing = db.query(Cliente).filter(Cliente.correo == data.correo).first()
        if existing:
            raise HTTPException(status_code=409, detail="Correo ya registrado")
        
        # ya no se hace hashing
        nuevo_cliente = Cliente(
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            telefono=data.telefono,
            contrasena=data.contrasena  # texto plano
        )
        
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        
        return ClienteResponseSchema(
            id_cliente=nuevo_cliente.id_cliente,
            nombre=nuevo_cliente.nombre,
            apellido=nuevo_cliente.apellido,
            correo=nuevo_cliente.correo,
            telefono=nuevo_cliente.telefono,
            fecha_registro=nuevo_cliente.fecha_registro
        )

    @staticmethod
    def login_cliente(db: Session, correo: str, contrasena: str) -> ClienteResponseSchema:
        """Login comparando texto plano"""
        cliente = db.query(Cliente).filter(Cliente.correo == correo).first()
        
        if not cliente or cliente.contrasena != contrasena:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
        
        return ClienteResponseSchema(
            id_cliente=cliente.id_cliente,
            nombre=cliente.nombre,
            apellido=cliente.apellido,
            correo=cliente.correo,
            telefono=cliente.telefono,
            fecha_registro=cliente.fecha_registro
        )

    
    @staticmethod
    def crear_direccion(db: Session, id_cliente: int, data: DireccionCreateSchema) -> DireccionResponseSchema:
        """Crea una nueva dirección para un cliente"""
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        nueva_direccion = Direccion(
            id_cliente=id_cliente,
            calle=data.calle,
            ciudad=data.ciudad,
            estado=data.estado,
            codigo_postal=data.codigo_postal,
            referencias=data.referencias
        )
        
        db.add(nueva_direccion)
        db.commit()
        db.refresh(nueva_direccion)
        
        return DireccionResponseSchema.from_orm(nueva_direccion)
    
    @staticmethod
    def obtener_direcciones_cliente(db: Session, id_cliente: int) -> list[DireccionResponseSchema]:
        """Obtiene todas las direcciones de un cliente"""
        direcciones = db.query(Direccion).filter(Direccion.id_cliente == id_cliente).all()
        return [DireccionResponseSchema.from_orm(d) for d in direcciones]

    
    @staticmethod
    def obtener_productos(db: Session) -> list[ProductoResponseSchema]:
        """Obtiene todos los productos activos"""
        productos = db.query(Producto).filter(Producto.activo == True).all()
        return [ProductoResponseSchema.from_orm(p) for p in productos]
    
    @staticmethod
    def obtener_producto(db: Session, id_producto: int) -> ProductoResponseSchema:
        """Obtiene un producto por ID"""
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return ProductoResponseSchema.from_orm(producto)
    
    @staticmethod
    def crear_producto(db: Session, data: ProductoCreateSchema) -> ProductoResponseSchema:
        """Crea un nuevo producto"""
        categoria = db.query(Categoria).filter(Categoria.id_categoria == data.id_categoria).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
        nuevo_producto = Producto(
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio=data.precio,
            stock=data.stock,
            id_categoria=data.id_categoria,
            imagen_url=data.imagen_url
        )
        
        db.add(nuevo_producto)
        db.commit()
        db.refresh(nuevo_producto)
        
        return ProductoResponseSchema.from_orm(nuevo_producto)
    
    @staticmethod
    def actualizar_producto(db: Session, id_producto: int, data: ProductoUpdateSchema) -> ProductoResponseSchema:
        """Actualiza un producto"""
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if data.nombre is not None:
            producto.nombre = data.nombre
        if data.descripcion is not None:
            producto.descripcion = data.descripcion
        if data.precio is not None:
            producto.precio = data.precio
        if data.stock is not None:
            producto.stock = data.stock
        if data.id_categoria is not None:
            producto.id_categoria = data.id_categoria
        if data.imagen_url is not None:
            producto.imagen_url = data.imagen_url
        if data.activo is not None:
            producto.activo = data.activo
        
        db.commit()
        db.refresh(producto)
        
        return ProductoResponseSchema.from_orm(producto)
    
    @staticmethod
    def obtener_categorias(db: Session) -> list[CategoriaResponseSchema]:
        """Obtiene todas las categorías"""
        categorias = db.query(Categoria).all()
        return [CategoriaResponseSchema.from_orm(c) for c in categorias]

    @staticmethod
    def agregar_al_carrito(db: Session, data: CarritoAgregarSchema) -> CarritoResponseSchema:
        """Agrega un producto al carrito del cliente"""
        cliente = db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        producto = db.query(Producto).filter(Producto.id_producto == data.id_producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if producto.stock < data.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente. Disponible: {producto.stock}")
        
        carrito = db.query(Carrito).filter(Carrito.id_cliente == data.id_cliente).first()
        if not carrito:
            carrito = Carrito(id_cliente=data.id_cliente)
            db.add(carrito)
            db.commit()
            db.refresh(carrito)

        item_existente = db.query(Carrito_Item).filter(
            Carrito_Item.id_carrito == carrito.id_carrito,
            Carrito_Item.id_producto == data.id_producto
        ).first()
        
        if item_existente:
            item_existente.cantidad += data.cantidad
        else:
            nuevo_item = Carrito_Item(
                id_carrito=carrito.id_carrito,
                id_producto=data.id_producto,
                cantidad=data.cantidad,
                precio_unitario=producto.precio
            )
            db.add(nuevo_item)
        
        db.commit()
        
        return SistemaServices.obtener_carrito(db, data.id_cliente)
    
    @staticmethod
    def obtener_carrito(db: Session, id_cliente: int) -> CarritoResponseSchema:
        """Obtiene el carrito de un cliente"""
        carrito = db.query(Carrito).filter(Carrito.id_cliente == id_cliente).first()
        
        if not carrito:
            raise HTTPException(status_code=404, detail="Carrito no encontrado")
        
        items_response = []
        total = 0.0
        
        for item in carrito.items:
            subtotal = float(item.precio_unitario) * item.cantidad
            total += subtotal
            
            items_response.append(CarritoItemResponseSchema(
                id_item=item.id_item,
                id_producto=item.id_producto,
                nombre_producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario),
                subtotal=subtotal
            ))
        
        return CarritoResponseSchema(
            id_carrito=carrito.id_carrito,
            id_cliente=carrito.id_cliente,
            items=items_response,
            total=total
        )
    
    @staticmethod
    def eliminar_item_carrito(db: Session, id_item: int):
        """Elimina un item del carrito"""
        item = db.query(Carrito_Item).filter(Carrito_Item.id_item == id_item).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item no encontrado")
        
        db.delete(item)
        db.commit()
        
        return {"message": "Item eliminado del carrito"}

    
    @staticmethod
    def crear_pedido(db: Session, data: PedidoCreateSchema) -> PedidoResponseSchema:
        """Crea un pedido a partir del carrito del cliente"""
        carrito = db.query(Carrito).filter(Carrito.id_cliente == data.id_cliente).first()
        
        if not carrito or not carrito.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")

        direccion = db.query(Direccion).filter(Direccion.id_direccion == data.id_direccion).first()
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        
        total = Decimal(0)
        for item in carrito.items:
            producto = item.producto
            if producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                )
            total += item.precio_unitario * item.cantidad

        nuevo_pedido = Pedido(
            id_cliente=data.id_cliente,
            id_direccion=data.id_direccion,
            total=total,
            estado="PENDIENTE"
        )
        
        db.add(nuevo_pedido)
        db.flush()

        for item in carrito.items:
            pedido_item = Pedido_Item(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=item.id_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            db.add(pedido_item)
        
        db.commit()
        db.refresh(nuevo_pedido)
        
        return SistemaServices.obtener_pedido(db, nuevo_pedido.id_pedido)
    
    @staticmethod
    def obtener_pedido(db: Session, id_pedido: int) -> PedidoResponseSchema:
        """Obtiene un pedido por ID"""
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        items_response = []
        for item in pedido.items:
            subtotal = float(item.precio_unitario) * item.cantidad
            items_response.append(PedidoItemResponseSchema(
                id_pedido_item=item.id_pedido_item,
                id_producto=item.id_producto,
                nombre_producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario),
                subtotal=subtotal
            ))
        
        return PedidoResponseSchema(
            id_pedido=pedido.id_pedido,
            id_cliente=pedido.id_cliente,
            id_direccion=pedido.id_direccion,
            total=float(pedido.total),
            estado=pedido.estado,
            fecha_creacion=pedido.fecha_creacion,
            items=items_response
        )
    
    @staticmethod
    async def procesar_pago(db: Session, id_pedido: int, numero_tarjeta_origen: str, 
                           nombre_cliente: str, mes_exp: int, anio_exp: int, cvv: str):
        """Procesa el pago de un pedido enviando solicitud al banco"""
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        if pedido.estado != "PENDIENTE":
            raise HTTPException(status_code=400, detail=f"El pedido ya fue procesado. Estado: {pedido.estado}")
        
        nuevo_pago = Pago(
            id_pedido=id_pedido,
            estado="PENDIENTE",
            monto=pedido.total,
            moneda="MXN",
            metodo="TARJETA"
        )
        
        db.add(nuevo_pago)
        db.flush()

        solicitud_banco = BancoSolicitudSchema(
            NumeroTarjetaOrigen=numero_tarjeta_origen,
            NumeroTarjetaDestino=TARJETA_DESTINO_COMERCIO,
            NombreCliente=nombre_cliente,
            MesExp=mes_exp,
            AnioExp=anio_exp,
            Cvv=cvv,
            Monto=float(pedido.total),
            Moneda="MXN"
        )

        pago_solicitud = Pago_Solicitud(
            id_pago=nuevo_pago.id_pago,
            numero_tarjeta_origen=numero_tarjeta_origen,
            numero_tarjeta_destino=TARJETA_DESTINO_COMERCIO,
            nombre_cliente=nombre_cliente,
            mes_exp=mes_exp,
            anio_exp=anio_exp,
            cvv=cvv,
            monto=pedido.total,
            moneda="MXN",
            tipo="TRANSFERENCIA",
            request_json=solicitud_banco.json()
        )
        
        db.add(pago_solicitud)
        db.commit()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    BANCO_API_URL,
                    json=solicitud_banco.dict(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    respuesta_banco = response.json()
                    
                    pago_respuesta = Pago_Respuesta(
                        id_pago=nuevo_pago.id_pago,
                        nombre_comercio=respuesta_banco.get("NombreComercio"),
                        creada_utc=datetime.fromisoformat(respuesta_banco.get("CreadaUTC").replace("Z", "+00:00")) if respuesta_banco.get("CreadaUTC") else None,
                        id_transaccion=respuesta_banco.get("IdTransaccion"),
                        tipo_transaccion=respuesta_banco.get("TipoTransaccion"),
                        monto_transaccion=respuesta_banco.get("MontoTransaccion"),
                        moneda=respuesta_banco.get("Moneda"),
                        marca_tarjeta=respuesta_banco.get("MarcaTarjeta"),
                        numero_tarjeta=respuesta_banco.get("NumeroTarjeta"),
                        numero_autorizacion=respuesta_banco.get("NumeroAutorizacion"),
                        nombre_estado=respuesta_banco.get("NombreEstado"),
                        firma=respuesta_banco.get("Firma"),
                        mensaje=respuesta_banco.get("Mensaje"),
                        response_json=json.dumps(respuesta_banco)
                    )
                    
                    db.add(pago_respuesta)

                    estado_banco = respuesta_banco.get("NombreEstado", "").upper()
                    nuevo_pago.estado = estado_banco

                    if estado_banco == "ACEPTADA":
                        pedido.estado = "PAGADO"

                        for item in pedido.items:
                            producto = item.producto
                            producto.stock -= item.cantidad

                        carrito = db.query(Carrito).filter(Carrito.id_cliente == pedido.id_cliente).first()
                        if carrito:
                            for item in carrito.items:
                                db.delete(item)

                        await SistemaServices.notificar_envio(pedido, pedido.direccion)
                    
                    elif estado_banco == "RECHAZADA":
                        pedido.estado = "PAGO_FALLIDO"
                    
                    db.commit()
                    
                    return {
                        "message": "Pago procesado",
                        "estado_pago": nuevo_pago.estado,
                        "estado_pedido": pedido.estado,
                        "id_transaccion": respuesta_banco.get("IdTransaccion"),
                        "mensaje_banco": respuesta_banco.get("Mensaje")
                    }
                else:
                    raise HTTPException(status_code=500, detail="Error al comunicarse con el banco")
        
        except httpx.RequestError as e:
            nuevo_pago.estado = "ERROR"
            db.commit()
            raise HTTPException(status_code=503, detail=f"No se pudo conectar con el banco: {str(e)}")
    
    @staticmethod
    async def notificar_envio(pedido: Pedido, direccion: Direccion):
        """Notifica al sistema de envíos sobre un nuevo pedido pagado"""
        try:
            payload = {
                "id_pedido": pedido.id_pedido,
                "id_cliente": pedido.id_cliente,
                "direccion": {
                    "calle": direccion.calle,
                    "ciudad": direccion.ciudad,
                    "estado": direccion.estado,
                    "codigo_postal": direccion.codigo_postal,
                    "referencias": direccion.referencias
                },
                "productos": [
                    {
                        "id_producto": item.id_producto,
                        "nombre": item.producto.nombre,
                        "cantidad": item.cantidad
                    }
                    for item in pedido.items
                ],
                "total": float(pedido.total)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    ENVIOS_API_URL,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    print(f"Envío notificado correctamente para pedido {pedido.id_pedido}")
                else:
                    print(f"Error al notificar envío: {response.status_code}")
        
        except httpx.RequestError as e:
            print(f"❌ No se pudo conectar con sistema de envíos: {str(e)}")
    
    @staticmethod
    def actualizar_estado_envio(db: Session, id_pedido: int, nuevo_estado: str):
        """Actualiza el estado de envío de un pedido (webhook de envíos)"""
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        estados_validos = ["EN_ENVIO", "EN_REPARTO", "ENTREGADO"]
        if nuevo_estado not in estados_validos:
            raise HTTPException(status_code=400, detail=f"Estado inválido. Debe ser uno de: {estados_validos}")
        
        pedido.estado = nuevo_estado
        db.commit()
        
        return {
            "message": "Estado de envío actualizado",
            "id_pedido": id_pedido,
            "nuevo_estado": nuevo_estado
        }
    
    

    @staticmethod
    def consultar_disponibilidad(db: Session, id_producto: int):
        """
        Consulta la disponibilidad específica de un producto
        Para que otros sistemas puedan verificar antes de hacer pedidos
        """
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        disponibilidad = "DISPONIBLE" if producto.stock > 0 else "AGOTADO"
        nivel_stock = "ALTO" if producto.stock > 20 else "BAJO" if producto.stock > 0 else "AGOTADO"
        
        return {
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "stock_actual": producto.stock,
            "disponibilidad": disponibilidad,
            "nivel_stock": nivel_stock,
            "precio": float(producto.precio),
            "activo": producto.activo,
            "puede_ordenar": producto.activo and producto.stock > 0
        }


    @staticmethod
    def consultar_disponibilidad_multiple(db: Session, ids_productos: list[int]):
        """
        Consulta la disponibilidad de múltiples productos a la vez
        Útil cuando otros sistemas quieren verificar varios productos
        """
        resultados = []
        
        for id_producto in ids_productos:
            try:
                disponibilidad = SistemaServices.consultar_disponibilidad(db, id_producto)
                resultados.append(disponibilidad)
            except HTTPException:
                resultados.append({
                    "id_producto": id_producto,
                    "error": "Producto no encontrado"
                })
        
        return {
            "total_consultados": len(ids_productos),
            "productos": resultados
        }


    @staticmethod
    def obtener_todos_clientes(db: Session) -> list[ClienteResponseSchema]:
        """
        Obtiene todos los clientes registrados en el sistema
        Para consultas administrativas o de otros sistemas
        """
        clientes = db.query(Cliente).all()
        return [ClienteResponseSchema(
            id_cliente=c.id_cliente,
            nombre=c.nombre,
            apellido=c.apellido,
            correo=c.correo,
            telefono=c.telefono,
            fecha_registro=c.fecha_registro
        ) for c in clientes]
    
    @staticmethod
    def obtener_catalogo_completo(db: Session, store_id: int = 1, category: int = None):
        """
        🛒 CATÁLOGO PARA API DISTRIBUIDA
        
        Recibe:
        - store_id: ID de tu tienda
        - category: ID de categoría (opcional)
        
        Devuelve productos en formato:
        {
            "store_id": 1,
            "id": 5,
            "nombre": "Producto",
            "description": "...",
            "precio": 299.99,
            "talla": "M",
            "color": "Rojo",
            "stock": 10,
            "duracion_minutos": null
        }
        """
        # Query base: productos activos de esta tienda
        query = db.query(Producto).filter(
            Producto.activo == True,
            Producto.store_id == store_id
        )
        
        # Si enviaron categoría específica, filtrar por ella
        if category is not None:
            query = query.filter(Producto.id_categoria == category)
        
        productos = query.all()
        
        # Formatear respuesta según el formato que esperan otros equipos
        catalogo_productos = []
        for p in productos:
            catalogo_productos.append({
                "store_id": p.store_id,
                "id": p.id_producto,
                "nombre": p.nombre,
                "description": p.descripcion,
                "precio": float(p.precio),
                "talla": p.talla,
                "color": p.color,
                "stock": p.stock,
                "duracion_minutos": p.duracion_minutos
            })
        
        return catalogo_productos


    @staticmethod
    def obtener_catalogo_por_categoria(db: Session):
        """
        📂 Catálogo organizado por categorías
        
        Agrupa todos los productos por su categoría
        Útil para mostrar el catálogo organizado
        """
        categorias = db.query(Categoria).all()
        
        catalogo = {
            "total_categorias": len(categorias),
            "total_productos": 0,
            "fecha_consulta": datetime.now().isoformat(),
            "categorias": []
        }
        
        for categoria in categorias:
            productos = db.query(Producto).filter(
                Producto.id_categoria == categoria.id_categoria,
                Producto.activo == True
            ).all()
            
            productos_lista = []
            for producto in productos:
                if producto.stock == 0:
                    disponibilidad = "AGOTADO"
                    puede_ordenar = False
                elif producto.stock <= 5:
                    disponibilidad = "ULTIMAS_UNIDADES"
                    puede_ordenar = True
                else:
                    disponibilidad = "DISPONIBLE"
                    puede_ordenar = True
                
                productos_lista.append({
                    "id_producto": producto.id_producto,
                    "nombre": producto.nombre,
                    "descripcion": producto.descripcion,
                    "precio": float(producto.precio),
                    "stock_disponible": producto.stock,
                    "disponibilidad": disponibilidad,
                    "puede_ordenar": puede_ordenar,
                    "imagen_url": producto.imagen_url
                })
            
            if productos_lista:  # Solo agregar categorías que tengan productos
                catalogo["categorias"].append({
                    "id_categoria": categoria.id_categoria,
                    "nombre_categoria": categoria.nombre,
                    "descripcion": categoria.descripcion,
                    "total_productos": len(productos_lista),
                    "productos": productos_lista
                })
                catalogo["total_productos"] += len(productos_lista)
        
        return catalogo


    @staticmethod
    def consultar_disponibilidad(db: Session, id_producto: int):
        """
        🔍 Consulta disponibilidad de UN producto específico
        
        Para que otros sistemas verifiquen antes de hacer pedidos
        """
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Determinar disponibilidad y nivel de stock
        if producto.stock == 0:
            disponibilidad = "AGOTADO"
            nivel_stock = "SIN_STOCK"
            puede_ordenar = False
        elif producto.stock <= 5:
            disponibilidad = "ULTIMAS_UNIDADES"
            nivel_stock = "BAJO"
            puede_ordenar = True
        elif producto.stock <= 20:
            disponibilidad = "DISPONIBLE"
            nivel_stock = "MEDIO"
            puede_ordenar = True
        else:
            disponibilidad = "DISPONIBLE"
            nivel_stock = "ALTO"
            puede_ordenar = True
        
        return {
            "id_producto": producto.id_producto,
            "nombre": producto.nombre,
            "stock_disponible": producto.stock,
            "disponibilidad": disponibilidad,
            "nivel_stock": nivel_stock,
            "precio": float(producto.precio),
            "activo": producto.activo,
            "puede_ordenar": puede_ordenar and producto.activo
        }


    @staticmethod
    def consultar_disponibilidad_multiple(db: Session, ids_productos: list[int]):
        """
        🔍 Consulta disponibilidad de MÚLTIPLES productos
        
        Útil cuando otro sistema quiere verificar varios productos a la vez
        """
        resultados = []
        
        for id_producto in ids_productos:
            try:
                disponibilidad = SistemaServices.consultar_disponibilidad(db, id_producto)
                resultados.append(disponibilidad)
            except HTTPException:
                resultados.append({
                    "id_producto": id_producto,
                    "error": "Producto no encontrado",
                    "disponibilidad": "NO_EXISTE"
                })
        
        return {
            "total_consultados": len(ids_productos),
            "fecha_consulta": datetime.now().isoformat(),
            "productos": resultados
        }


    @staticmethod
    def obtener_todos_clientes(db: Session) -> list[ClienteResponseSchema]:
        """
        👥 Obtiene todos los clientes registrados
        
        Para consultas administrativas o integración con otros sistemas
        """
        clientes = db.query(Cliente).all()
        return [ClienteResponseSchema(
            id_cliente=c.id_cliente,
            nombre=c.nombre,
            apellido=c.apellido,
            correo=c.correo,
            telefono=c.telefono,
            fecha_registro=c.fecha_registro
        ) for c in clientes]


    @staticmethod
    def obtener_catalogo_api(db: Session, store_id: int, category: int = None):
        """
        🌐 ENDPOINT PARA API DISTRIBUIDA
        
        Este es el endpoint que otros equipos consultarán.
        
        Parámetros:
        - store_id: ID de tu tienda (siempre será 1 en tu caso)
        - category: ID de categoría (opcional, si no se envía devuelve todo)
        
        Devuelve productos en el formato específico que necesitan:
        {
            "store_id": 1,
            "id": 5,
            "nombre": "Producto X",
            "description": "Descripción...",
            "precio": 299.99,
            "talla": "M",
            "color": "Rojo",
            "stock": 10,
            "duracion_minutos": null
        }
        """
        # Query base: productos activos de esta tienda
        query = db.query(Producto).filter(
            Producto.activo == True,
            Producto.store_id == store_id
        )
        
        # Si enviaron categoría específica, filtrar por ella
        if category is not None:
            query = query.filter(Producto.id_categoria == category)
        
        productos = query.all()
        
        # Formatear respuesta según el schema que esperan
        catalogo = []
        for p in productos:
            catalogo.append({
                "store_id": p.store_id,
                "id": p.id_producto,
                "nombre": p.nombre,
                "description": p.descripcion,
                "precio": float(p.precio),
                "talla": p.talla,
                "color": p.color,
                "stock": p.stock,
                "duracion_minutos": p.duracion_minutos
            })
        
        return {
            "store_id": store_id,
            "category": category,
            "total_productos": len(catalogo),
            "productos": catalogo
        }
