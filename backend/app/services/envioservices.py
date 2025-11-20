import httpx
import json
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Envio import (
    Envio, 
    EnvioIniciarSchema, 
    EnvioSolicitudSchema, 
    EnvioRespuestaSchema, 
    EnvioResponseSchema,
    ProductoEnvioSchema,
    DatosClienteEnvioSchema
)
from app.models.Pedido import Pedido
from app.models.Cliente import Cliente
from app.models.Direccion import Direccion

ENVIOS_API_URL = "https://api-envios-equipo.onrender.com/api/envios/crear"


class EnvioServices:
    
    @staticmethod
    async def crear_envio(db: Session, datos: EnvioIniciarSchema):
        """
        📦 CREAR SOLICITUD DE ENVÍO
        
        Flujo:
        1. Buscar pedido (id_pedido) en BD
        2. Validar que tenga cliente y dirección
        3. Construir JSON de solicitud (SOL_ENV)
        4. Enviar a API externa
        5. Guardar respuesta (EDO_ENV)
        """
        
        # 1. Buscar el pedido con sus relaciones (items + productos)
        pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
        if not pedido:
            raise HTTPException(status_code=404, detail=f"Pedido {datos.id_pedido} no encontrado")
        
        # 2. Obtener cliente
        cliente = db.query(Cliente).filter(Cliente.id_cliente == pedido.id_cliente).first()
        if not cliente:
            raise HTTPException(
                status_code=404, 
                detail=f"Cliente {pedido.id_cliente} no encontrado para pedido {datos.id_pedido}"
            )
        
        # 3. Obtener dirección
        direccion = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
        if not direccion:
            raise HTTPException(
                status_code=404, 
                detail=f"Dirección {pedido.id_direccion} no encontrada para pedido {datos.id_pedido}"
            )
        
        # 4. Generar ID único para la orden externa
        # Formato: ECM-YYYY-00001
        id_orden_externa = f"ECM-{datetime.now().year}-{pedido.id_pedido:05d}"
        
        # 5. Preparar datos del cliente (SOL_ENV.datos_cliente)
        datos_cliente = DatosClienteEnvioSchema(
            nombre=f"{cliente.nombre} {cliente.apellido}",
            telefono=cliente.telefono or "Sin teléfono",
            email=cliente.correo,
            direccion_completa=direccion.calle,
            ciudad=direccion.ciudad,
            estado=direccion.estado,
            codigo_postal=direccion.codigo_postal
        )
        
        # 6. Preparar lista de productos (SOL_ENV.productos)
        # IMPORTANTE: Asume que Pedido tiene relación `items` con PedidoItem
        # y que PedidoItem tiene relación `producto` con Producto
        productos = []
        for item in pedido.items:
            productos.append(ProductoEnvioSchema(
                id_producto=item.id_producto,         # ID del producto
                nombre=item.producto.nombre,          # Nombre del producto (desde relación)
                cantidad=item.cantidad,               # Cantidad comprada
                precio=float(item.precio_unitario)    # Precio unitario
            ))
        
        # 7. Crear registro de envío en estado PENDIENTE (antes de enviar)
        envio = Envio(
            id_pedido=pedido.id_pedido,
            id_orden_externa=id_orden_externa,
            id_orden_original=pedido.id_pedido,  # ✅ CORREGIDO: Solo una vez aquí
            servicio_origen="ecommerce",
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        try:
            # 8. Construir solicitud completa (SOL_ENV)
            solicitud = EnvioSolicitudSchema(
                id_orden_externa=id_orden_externa,
                id_orden_original=pedido.id_pedido,
                servicio_origen="ecommerce",
                datos_cliente=datos_cliente,
                productos=productos
            )
            
            # Guardar JSON de solicitud (auditoría)
            envio.request_json = solicitud.model_dump_json()
            db.commit()
            
            # 9. Enviar solicitud a la API de envíos (POST)
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    ENVIOS_API_URL,
                    json=solicitud.model_dump()
                )
            
            # 10. Procesar respuesta (EDO_ENV)
            if response.status_code in [200, 201]:
                respuesta = response.json()
                
                # Validar que la respuesta tenga los campos esperados
                envio_resp = EnvioRespuestaSchema(**respuesta)
                
                # Actualizar registro de envío con datos recibidos
                envio.codigo_seguimiento = envio_resp.codigo_seguimiento
                envio.estado_actual = envio_resp.estado_actual
                envio.ubicacion_actual = envio_resp.ubicacion_actual
                
                # Convertir fecha (remover 'Z' si viene en formato ISO)
                envio.fecha_actualizacion = datetime.fromisoformat(
                    envio_resp.fecha_actualizacion.replace('Z', '+00:00')
                )
                
                # Guardar JSON completo de respuesta (auditoría)
                envio.response_json = json.dumps(respuesta)
                
            else:
                # Error de la API de envíos
                envio.estado_actual = "ERROR"
                envio.response_json = f"Error {response.status_code}: {response.text}"
            
            db.commit()
            db.refresh(envio)
            
            return EnvioResponseSchema.model_validate(envio)
            
        except Exception as e:
            # Error inesperado (timeout, conexión, etc.)
            envio.estado_actual = "ERROR"
            envio.response_json = f"Excepción: {str(e)}"
            db.commit()
            raise HTTPException(
                status_code=500, 
                detail=f"Error al crear envío: {str(e)}"
            )
    
    
    @staticmethod
    def consultar_envio(db: Session, id_envio: int):
        """🔍 Consultar estado de un envío por ID"""
        envio = db.query(Envio).filter(Envio.id_envio == id_envio).first()
        if not envio:
            raise HTTPException(status_code=404, detail="Envío no encontrado")
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def consultar_envio_por_pedido(db: Session, id_pedido: int):
        """🔍 Consultar envío de un pedido específico"""
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()
        if not envio:
            raise HTTPException(
                status_code=404, 
                detail=f"No hay envío registrado para el pedido {id_pedido}"
            )
        return EnvioResponseSchema.model_validate(envio)