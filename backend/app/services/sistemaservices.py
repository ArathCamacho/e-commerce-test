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

# Configuración de APIs externas
BANCO_API_URL = "http://localhost:5000/api/transacciones"
ENVIOS_API_URL = "http://localhost:6000/api/envios/crear"
TARJETA_DESTINO_COMERCIO = "0000 0009 8765 4321"


class SistemaServices:
    """
    Servicio principal del sistema de e-commerce
    Gestiona: Clientes, Productos, Carrito, Pedidos y Pagos
    """

    # ============================================
    # AUTENTICACIÓN Y CLIENTES
    # ============================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Devuelve la contraseña sin hash (para desarrollo)"""
        if not isinstance(password, str):
            password = str(password, "utf-8") if isinstance(password, bytes) else str(password)
        password = password.strip()
        if not password:
            raise HTTPException(status_code=400, detail="La contraseña no puede estar vacía")
        return password

    @staticmethod
    def verificar_password(plain_password: str, hash_password: str) -> bool:
        """Compara contraseñas en texto plano"""
        return plain_password == hash_password

    @staticmethod
    def registrar_cliente(db: Session, data: ClienteRegistroSchema) -> ClienteResponseSchema:
        """Registra un nuevo cliente"""
        if db.query(Cliente).filter(Cliente.correo == data.correo).first():
            raise HTTPException(status_code=409, detail="Correo ya registrado")
        
        nuevo_cliente = Cliente(
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            telefono=data.telefono,
            contrasena=data.contrasena
        )
        
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        
        return ClienteResponseSchema.from_orm(nuevo_cliente)

    @staticmethod
    def login_cliente(db: Session, correo: str, contrasena: str) -> ClienteResponseSchema:
        """Autentica un cliente"""
        cliente = db.query(Cliente).filter(Cliente.correo == correo).first()
        
        if not cliente or cliente.contrasena != contrasena:
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
        
        return ClienteResponseSchema.from_orm(cliente)

    @staticmethod
    def obtener_todos_clientes(db: Session) -> list[ClienteResponseSchema]:
        """Obtiene todos los clientes (uso administrativo)"""
        clientes = db.query(Cliente).all()
        return [ClienteResponseSchema.from_orm(c) for c in clientes]

    # ============================================
    # DIRECCIONES
    # ============================================

    @staticmethod
    def crear_direccion(db: Session, id_cliente: int, data: DireccionCreateSchema) -> DireccionResponseSchema:
        """Crea una nueva dirección para un cliente"""
        if not db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first():
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

    # ============================================
    # CATEGORÍAS (FUNDAMENTALES)
    # ============================================

    @staticmethod
    def obtener_categorias(db: Session) -> list[CategoriaResponseSchema]:
        """Obtiene todas las categorías del sistema"""
        categorias = db.query(Categoria).all()
        return [CategoriaResponseSchema.from_orm(c) for c in categorias]

    # ============================================
    # PRODUCTOS Y CATÁLOGO
    # ============================================

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
        if not db.query(Categoria).filter(Categoria.id_categoria == data.id_categoria).first():
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
        """Actualiza un producto existente"""
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        campos_actualizables = ['nombre', 'descripcion', 'precio', 'stock', 'id_categoria', 'imagen_url', 'activo']
        for campo in campos_actualizables:
            valor = getattr(data, campo, None)
            if valor is not None:
                setattr(producto, campo, valor)
        
        db.commit()
        db.refresh(producto)
        
        return ProductoResponseSchema.from_orm(producto)

    @staticmethod
    def _calcular_disponibilidad(stock: int) -> tuple[str, str, bool]:
        """Calcula el estado de disponibilidad de un producto"""
        if stock == 0:
            return "AGOTADO", "SIN_STOCK", False
        elif stock <= 5:
            return "ULTIMAS_UNIDADES", "BAJO", True
        elif stock <= 20:
            return "DISPONIBLE", "MEDIO", True
        return "DISPONIBLE", "ALTO", True

    @staticmethod
    def consultar_disponibilidad(db: Session, id_producto: int):
        """Consulta disponibilidad de un producto específico"""
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        disponibilidad, nivel_stock, puede_ordenar = SistemaServices._calcular_disponibilidad(producto.stock)
        
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
        """Consulta disponibilidad de múltiples productos"""
        resultados = []
        for id_producto in ids_productos:
            try:
                resultados.append(SistemaServices.consultar_disponibilidad(db, id_producto))
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
    def obtener_catalogo_por_categoria(db: Session):
        """Obtiene el catálogo completo organizado por categorías"""
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
            
            if not productos:
                continue
            
            productos_lista = []
            for producto in productos:
                disponibilidad, _, puede_ordenar = SistemaServices._calcular_disponibilidad(producto.stock)
                
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
    def obtener_catalogo_api(db: Session, store_id: int, category: int = None):
        """
        Endpoint para API distribuida
        Formato específico para integración con otros sistemas
        """
        query = db.query(Producto).filter(
            Producto.activo == True,
            Producto.store_id == store_id
        )
        
        if category is not None:
            query = query.filter(Producto.id_categoria == category)
        
        productos = query.all()
        
        catalogo = [{
            "store_id": p.store_id,
            "id": p.id_producto,
            "nombre": p.nombre,
            "description": p.descripcion,
            "precio": float(p.precio),
            "talla": p.talla,
            "color": p.color,
            "stock": p.stock,
            "duracion_minutos": p.duracion_minutos
        } for p in productos]
        
        return {
            "store_id": store_id,
            "category": category,
            "total_productos": len(catalogo),
            "productos": catalogo
        }

    # ============================================
    # CARRITO DE COMPRAS
    # ============================================

    @staticmethod
    def agregar_al_carrito(db: Session, data: CarritoAgregarSchema) -> CarritoResponseSchema:
        """Agrega un producto al carrito del cliente"""
        if not db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first():
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

    # ============================================
    # PEDIDOS
    # ============================================

    @staticmethod
    def crear_pedido(db: Session, data: PedidoCreateSchema) -> PedidoResponseSchema:
        """Crea un pedido a partir del carrito del cliente"""
        carrito = db.query(Carrito).filter(Carrito.id_cliente == data.id_cliente).first()
        if not carrito or not carrito.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")

        if not db.query(Direccion).filter(Direccion.id_direccion == data.id_direccion).first():
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        
        # Validar stock antes de crear el pedido
        total = Decimal(0)
        for item in carrito.items:
            if item.producto.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {item.producto.nombre}. Disponible: {item.producto.stock}"
                )
            total += item.precio_unitario * item.cantidad

        # Crear pedido
        nuevo_pedido = Pedido(
            id_cliente=data.id_cliente,
            id_direccion=data.id_direccion,
            total=total,
            estado="PENDIENTE"
        )
        db.add(nuevo_pedido)
        db.flush()

        # Crear items del pedido
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
        
        items_response = [
            PedidoItemResponseSchema(
                id_pedido_item=item.id_pedido_item,
                id_producto=item.id_producto,
                nombre_producto=item.producto.nombre,
                cantidad=item.cantidad,
                precio_unitario=float(item.precio_unitario),
                subtotal=float(item.precio_unitario) * item.cantidad
            )
            for item in pedido.items
        ]
        
        return PedidoResponseSchema(
            id_pedido=pedido.id_pedido,
            id_cliente=pedido.id_cliente,
            id_direccion=pedido.id_direccion,
            total=float(pedido.total),
            estado=pedido.estado,
            fecha_creacion=pedido.fecha_creacion,
            items=items_response
        )

    # ============================================
    # PAGOS Y PROCESAMIENTO
    # ============================================

    @staticmethod
    async def procesar_pago(db: Session, id_pedido: int, numero_tarjeta_origen: str, 
                           nombre_cliente: str, mes_exp: int, anio_exp: int, cvv: str):
        """Procesa el pago de un pedido enviando solicitud al banco"""
        pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        if pedido.estado != "PENDIENTE":
            raise HTTPException(status_code=400, detail=f"El pedido ya fue procesado. Estado: {pedido.estado}")
        
        # Crear registro de pago
        nuevo_pago = Pago(
            id_pedido=id_pedido,
            estado="PENDIENTE",
            monto=pedido.total,
            moneda="MXN",
            metodo="TARJETA"
        )
        db.add(nuevo_pago)
        db.flush()

        # Preparar solicitud al banco
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
                    
                    # Guardar respuesta del banco
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

                        # Reducir stock de productos
                        for item in pedido.items:
                            item.producto.stock -= item.cantidad

                        # Vaciar carrito
                        carrito = db.query(Carrito).filter(Carrito.id_cliente == pedido.id_cliente).first()
                        if carrito:
                            for item in carrito.items:
                                db.delete(item)

                        # Notificar sistema de envíos
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

    # ============================================
    # INTEGRACIÓN CON SISTEMA DE ENVÍOS
    # ============================================

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
                response = await client.post(ENVIOS_API_URL, json=payload, timeout=30.0)
                
                if response.status_code == 200:
                    print(f"✅ Envío notificado correctamente para pedido {pedido.id_pedido}")
                else:
                    print(f"⚠️ Error al notificar envío: {response.status_code}")
        
        except httpx.RequestError as e:
            print(f"❌ No se pudo conectar con sistema de envíos: {str(e)}")

    @staticmethod
    def actualizar_estado_envio(db: Session, id_pedido: int, nuevo_estado: str):
        """Actualiza el estado de envío de un pedido (webhook desde sistema de envíos)"""
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