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
        
        1. Busca el pedido en la BD
        2. Obtiene datos del cliente y productos
        3. Envía solicitud a la API de envíos
        4. Guarda la respuesta
        """
        
        # 1. Buscar el pedido con sus relaciones
        pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # 2. Obtener cliente y dirección
        cliente = db.query(Cliente).filter(Cliente.id_cliente == pedido.id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        direccion = db.query(Direccion).filter(Direccion.id_direccion == pedido.id_direccion).first()
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        
        # 3. Generar ID único para la orden
        id_orden_externa = f"ECM-{datetime.now().year}-{pedido.id_pedido:05d}"
        
        # 4. Preparar datos del cliente
        datos_cliente = DatosClienteEnvioSchema(
            nombre=f"{cliente.nombre} {cliente.apellido}",
            telefono=cliente.telefono or "Sin teléfono",
            email=cliente.correo,
            direccion_completa=direccion.calle,
            ciudad=direccion.ciudad,
            estado=direccion.estado,
            codigo_postal=direccion.codigo_postal
        )

        
        # 5. Preparar lista de productos
        productos = []
        for item in pedido.items:
            productos.append(ProductoEnvioSchema(
                id_producto=item.id_producto,
                nombre=item.producto.nombre,
                cantidad=item.cantidad,
                precio=float(item.precio_unitario)
            ))
        
        # 6. Crear registro de envío en estado PENDIENTE
        envio = Envio(
            id_pedido=pedido.id_pedido,
            id_orden_externa=id_orden_externa,
            id_orden_original=pedido.id_pedido,
            servicio_origen="ecommerce",
            estado_actual="PENDIENTE"
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        
        try:
            # 7. Preparar solicitud completa
            solicitud = EnvioSolicitudSchema(
                id_orden_externa=id_orden_externa,
                id_orden_original=pedido.id_pedido,
                servicio_origen="ecommerce",
                datos_cliente=datos_cliente,
                productos=productos
            )
            
            # Guardar lo que enviaste (auditoría)
            envio.request_json = solicitud.model_dump_json()
            
            # 8. Enviar a la API de envíos
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    ENVIOS_API_URL,
                    json=solicitud.model_dump()
                )
            
            # 9. Procesar respuesta
            if response.status_code == 200 or response.status_code == 201:
                respuesta = response.json()
                envio_resp = EnvioRespuestaSchema(**respuesta)
                
                # Guardar datos de la respuesta
                envio.codigo_seguimiento = envio_resp.codigo_seguimiento
                envio.estado_actual = envio_resp.estado_actual
                envio.ubicacion_actual = envio_resp.ubicacion_actual
                envio.fecha_actualizacion = datetime.fromisoformat(
                    envio_resp.fecha_actualizacion.replace('Z', '')
                )
                envio.response_json = json.dumps(respuesta)
                
            else:
                # Error en la API de envíos
                envio.estado_actual = "ERROR"
                envio.response_json = response.text
            
            db.commit()
            db.refresh(envio)
            
            return EnvioResponseSchema.model_validate(envio)
            
        except Exception as e:
            envio.estado_actual = "ERROR"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error al crear envío: {str(e)}")
    
    
    @staticmethod
    def consultar_envio(db: Session, id_envio: int):
        """🔍 Consultar estado de un envío"""
        envio = db.query(Envio).filter(Envio.id_envio == id_envio).first()
        if not envio:
            raise HTTPException(status_code=404, detail="Envío no encontrado")
        return EnvioResponseSchema.model_validate(envio)
    
    
    @staticmethod
    def consultar_envio_por_pedido(db: Session, id_pedido: int):
        """🔍 Consultar envío de un pedido específico"""
        envio = db.query(Envio).filter(Envio.id_pedido == id_pedido).first()
        if not envio:
            raise HTTPException(status_code=404, detail="Envío no encontrado para este pedido")
        return EnvioResponseSchema.model_validate(envio)