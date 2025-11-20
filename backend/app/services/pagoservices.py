import httpx
import json
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Pago import Pago, PagoIniciarSchema, BancoSolicitudSchema, BancoRespuestaSchema, PagoResponseSchema
from app.models.Pedido import Pedido  # 👈 AGREGADO

# 🔴 CAMBIA ESTAS URLs POR LAS REALES
BANCO_API_URL = "https://api-banco-equipo.onrender.com/api/transacciones"
TARJETA_COMERCIO = "0000000987654321"  # Sin espacios para la API

class PagoServices:
    
    @staticmethod
    async def procesar_pago(db: Session, datos: PagoIniciarSchema):
        """
        💳 PROCESAR PAGO CON BANCO
        
        Flujo:
        1. Valida que el pedido exista (si se proporciona)
        2. Crea registro de pago en PENDIENTE
        3. Envía solicitud al banco
        4. Actualiza estado según respuesta
        5. Si es APROBADO, actualiza el pedido a PAGADO
        """
        
        # 1. Validar pedido si viene en la solicitud
        pedido = None
        if datos.id_pedido:
            pedido = db.query(Pedido).filter(Pedido.id_pedido == datos.id_pedido).first()
            if not pedido:
                raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
            # Verificar que el monto coincida
            if float(pedido.total) != datos.monto:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El monto no coincide. Pedido: {pedido.total}, Solicitud: {datos.monto}"
                )
        
        # 2. Crear pago en PENDIENTE
        pago = Pago(
            id_pedido=datos.id_pedido,
            numero_tarjeta_origen=datos.numero_tarjeta_origen,
            nombre_cliente=datos.nombre_cliente,
            monto=Decimal(str(datos.monto)),
            moneda=datos.moneda,
            estado="PENDIENTE"
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        
        try:
            # 3. Preparar solicitud para el banco
            # Limpiar número de tarjeta (quitar espacios)
            tarjeta_limpia = datos.numero_tarjeta_origen.replace(" ", "")
            
            solicitud = BancoSolicitudSchema(
                numero_tarjeta_origen=tarjeta_limpia,
                numero_tarjeta_destino=TARJETA_COMERCIO,
                nombre_cliente=datos.nombre_cliente,
                mes_exp=datos.mes_exp,
                anio_exp=datos.anio_exp,
                cvv=datos.cvv,
                monto=datos.monto,
                moneda=datos.moneda
            )
            
            # Guardar lo que enviaste (auditoría)
            pago.request_json = solicitud.model_dump_json()
            
            # 4. Enviar al banco
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    BANCO_API_URL,
                    json=solicitud.model_dump()
                )
            
            # 5. Procesar respuesta
            if response.status_code == 200 or response.status_code == 201:
                respuesta = response.json()
                banco = BancoRespuestaSchema(**respuesta)
                
                # Guardar datos del banco
                if banco.creada_utc:
                    pago.creada_utc = datetime.fromisoformat(
                        banco.creada_utc.replace('Z', '')
                    )
                
                pago.id_transaccion = banco.id_transaccion
                pago.tipo = banco.tipo
                pago.numero_tarjeta = banco.numero_tarjeta
                pago.id_estado_transaccion = banco.id_estado_transaccion
                pago.firma = banco.firma
                pago.response_json = json.dumps(respuesta)
                
                # Actualizar estado según respuesta del banco
                if banco.id_estado_transaccion == 1:
                    pago.estado = "APROBADO"
                    # 6. Actualizar estado del pedido
                    if pedido:
                        pedido.estado = "PAGADO"
                elif banco.id_estado_transaccion == 2:
                    pago.estado = "RECHAZADO"
                    if pedido:
                        pedido.estado = "PAGO_RECHAZADO"
                else:
                    pago.estado = "PENDIENTE"
            else:
                # Error en la API del banco
                pago.estado = "ERROR"
                pago.response_json = response.text
            
            db.commit()
            db.refresh(pago)
            
            return PagoResponseSchema.model_validate(pago)
            
        except httpx.TimeoutException:
            pago.estado = "ERROR"
            pago.response_json = json.dumps({"error": "Timeout al conectar con el banco"})
            db.commit()
            raise HTTPException(status_code=504, detail="Timeout al procesar pago")
            
        except Exception as e:
            pago.estado = "ERROR"
            pago.response_json = json.dumps({"error": str(e)})
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error al procesar pago: {str(e)}")
    
    
    @staticmethod
    def consultar_pago(db: Session, id_pago: int):
        """🔍 Consultar estado de un pago"""
        pago = db.query(Pago).filter(Pago.id_pago == id_pago).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return PagoResponseSchema.model_validate(pago)
    
    
    @staticmethod
    def consultar_pagos_por_pedido(db: Session, id_pedido: int):
        """🔍 Consultar todos los pagos de un pedido"""
        pagos = db.query(Pago).filter(Pago.id_pedido == id_pedido).all()
        if not pagos:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron pagos para este pedido"
            )
        return [PagoResponseSchema.model_validate(p) for p in pagos]