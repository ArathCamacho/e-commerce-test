import httpx
import json
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.Pago import Pago, PagoIniciarSchema, BancoSolicitudSchema, BancoRespuestaSchema, PagoResponseSchema


BANCO_API_URL = "http://localhost:5000/api/transacciones"  # 🔴 CAMBIAR
TARJETA_COMERCIO = "0000 0009 8765 4321"  # 🔴 CAMBIAR

class PagoServices:
    
    @staticmethod
    async def procesar_pago(db: Session, datos: PagoIniciarSchema):
        # Crear pago en PENDIENTE
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
            # Preparar solicitud
            solicitud = BancoSolicitudSchema(
                numero_tarjeta_origen=datos.numero_tarjeta_origen,
                numero_tarjeta_destino=TARJETA_COMERCIO,
                nombre_cliente=datos.nombre_cliente,
                mes_exp=datos.mes_exp,
                anio_exp=datos.anio_exp,
                cvv=datos.cvv,
                monto=datos.monto,
                moneda=datos.moneda
            )
            pago.request_json = solicitud.model_dump_json()
            
            # Enviar al banco
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    BANCO_API_URL,
                    json=solicitud.model_dump()
                )
            
            # Procesar respuesta
            if response.status_code == 200:
                respuesta = response.json()
                banco = BancoRespuestaSchema(**respuesta)
                
                pago.creada_utc = datetime.fromisoformat(banco.creada_utc.replace('Z', '')) if banco.creada_utc else None
                pago.id_transaccion = banco.id_transaccion
                pago.tipo = banco.tipo
                pago.numero_tarjeta = banco.numero_tarjeta
                pago.id_estado_transaccion = banco.id_estado_transaccion
                pago.firma = banco.firma
                pago.response_json = json.dumps(respuesta)
                pago.estado = "APROBADO" if banco.id_estado_transaccion == 1 else "RECHAZADO"
            else:
                pago.estado = "ERROR"
                pago.response_json = response.text
            
            db.commit()
            db.refresh(pago)
            
            return PagoResponseSchema.model_validate(pago)
            
        except Exception as e:
            pago.estado = "ERROR"
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @staticmethod
    def consultar_pago(db: Session, id_pago: int):
        pago = db.query(Pago).filter(Pago.id_pago == id_pago).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        return PagoResponseSchema.model_validate(pago)