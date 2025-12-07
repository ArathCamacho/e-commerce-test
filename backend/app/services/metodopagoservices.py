from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.MetodoPago import MetodoPago, MetodoPagoCreateSchema, MetodoPagoResponseSchema, MetodoPagoUpdateSchema
from app.models.Cliente import Cliente
import logging

logger = logging.getLogger(__name__)

class MetodoPagoServices:

    @staticmethod
    def obtener_tarjetas_cliente(db: Session, id_cliente: int) -> list[MetodoPagoResponseSchema]:
        """Obtener todas las tarjetas de un cliente"""
        tarjetas = db.query(MetodoPago).filter(MetodoPago.id_cliente == id_cliente).all()

        # Enmascarar números de tarjeta
        result = []
        for tarjeta in tarjetas:
            # Mantener solo los últimos 4 dígitos
            masked_number = f"**** **** **** **{tarjeta.card_number[-2:]}" if len(tarjeta.card_number) >= 4 else "**** **** **** ****"

            result.append(MetodoPagoResponseSchema(
                id=tarjeta.id_metodo_pago,
                id_cliente=tarjeta.id_cliente,
                cardholderName=tarjeta.cardholder_name,
                cardNumber=masked_number,
                expiryDate=tarjeta.expiry_date,
                isDefault=tarjeta.is_default,
                fecha_creacion=tarjeta.fecha_creacion,
                ultima_actualizacion=tarjeta.ultima_actualizacion
            ))

        return result

    @staticmethod
    def agregar_tarjeta(db: Session, id_cliente: int, datos: MetodoPagoCreateSchema) -> MetodoPagoResponseSchema:
        """Agregar nueva tarjeta para un cliente"""
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Si es la primera tarjeta o está marcada como default, hacerla default
        existing_cards = db.query(MetodoPago).filter(MetodoPago.id_cliente == id_cliente).count()
        is_default = datos.isDefault or existing_cards == 0

        # Si está marcada como default, quitar el default de otras tarjetas
        if is_default:
            db.query(MetodoPago).filter(
                MetodoPago.id_cliente == id_cliente,
                MetodoPago.is_default == True
            ).update({"is_default": False})

        # Crear nueva tarjeta
        nueva_tarjeta = MetodoPago(
            id_cliente=id_cliente,
            cardholder_name=datos.cardholderName,
            card_number=datos.cardNumber,  # En producción debería encriptarse
            expiry_date=datos.expiryDate,
            cvv=datos.cvv,  # En producción debería encriptarse
            is_default=is_default
        )

        db.add(nueva_tarjeta)
        db.commit()
        db.refresh(nueva_tarjeta)

        logger.info(f"Tarjeta agregada para cliente {id_cliente}")

        # Retornar con número enmascarado
        masked_number = f"**** **** **** **{nueva_tarjeta.card_number[-2:]}" if len(nueva_tarjeta.card_number) >= 4 else "**** **** **** ****"

        return MetodoPagoResponseSchema(
            id=nueva_tarjeta.id_metodo_pago,
            id_cliente=nueva_tarjeta.id_cliente,
            cardholderName=nueva_tarjeta.cardholder_name,
            cardNumber=masked_number,
            expiryDate=nueva_tarjeta.expiry_date,
            isDefault=nueva_tarjeta.is_default,
            fecha_creacion=nueva_tarjeta.fecha_creacion,
            ultima_actualizacion=nueva_tarjeta.ultima_actualizacion
        )

    @staticmethod
    def actualizar_tarjeta(db: Session, id_cliente: int, id_tarjeta: int, datos: MetodoPagoUpdateSchema) -> MetodoPagoResponseSchema:
        """Actualizar tarjeta existente"""
        tarjeta = db.query(MetodoPago).filter(
            MetodoPago.id_metodo_pago == id_tarjeta,
            MetodoPago.id_cliente == id_cliente
        ).first()

        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

        # Actualizar campos proporcionados
        update_data = {}
        if datos.cardholderName is not None:
            update_data["cardholder_name"] = datos.cardholderName
        if datos.cardNumber is not None:
            update_data["card_number"] = datos.cardNumber
        if datos.expiryDate is not None:
            update_data["expiry_date"] = datos.expiryDate
        if datos.cvv is not None:
            update_data["cvv"] = datos.cvv
        if datos.isDefault is not None and datos.isDefault != tarjeta.is_default:
            update_data["is_default"] = datos.isDefault
            if datos.isDefault:
                # Quitar default de otras tarjetas
                db.query(MetodoPago).filter(
                    MetodoPago.id_cliente == id_cliente,
                    MetodoPago.id_metodo_pago != id_tarjeta,
                    MetodoPago.is_default == True
                ).update({"is_default": False})

        if update_data:
            db.query(MetodoPago).filter(MetodoPago.id_metodo_pago == id_tarjeta).update(update_data)
            db.commit()
            db.refresh(tarjeta)

        logger.info(f"Tarjeta {id_tarjeta} actualizada para cliente {id_cliente}")

        # Retornar con número enmascarado
        masked_number = f"**** **** **** **{tarjeta.card_number[-2:]}" if len(tarjeta.card_number) >= 4 else "**** **** **** ****"

        return MetodoPagoResponseSchema(
            id=tarjeta.id_metodo_pago,
            id_cliente=tarjeta.id_cliente,
            cardholderName=tarjeta.cardholder_name,
            cardNumber=masked_number,
            expiryDate=tarjeta.expiry_date,
            isDefault=tarjeta.is_default,
            fecha_creacion=tarjeta.fecha_creacion,
            ultima_actualizacion=tarjeta.ultima_actualizacion
        )

    @staticmethod
    def eliminar_tarjeta(db: Session, id_cliente: int, id_tarjeta: int):
        """Eliminar tarjeta"""
        tarjeta = db.query(MetodoPago).filter(
            MetodoPago.id_metodo_pago == id_tarjeta,
            MetodoPago.id_cliente == id_cliente
        ).first()

        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

        # Si era la default, hacer default otra tarjeta si existe
        if tarjeta.is_default:
            otra_tarjeta = db.query(MetodoPago).filter(
                MetodoPago.id_cliente == id_cliente,
                MetodoPago.id_metodo_pago != id_tarjeta
            ).first()
            if otra_tarjeta:
                otra_tarjeta.is_default = True

        db.delete(tarjeta)
        db.commit()

        logger.info(f"Tarjeta {id_tarjeta} eliminada para cliente {id_cliente}")
        return {"message": "Tarjeta eliminada correctamente"}

    @staticmethod
    def establecer_tarjeta_predeterminada(db: Session, id_cliente: int, id_tarjeta: int) -> MetodoPagoResponseSchema:
        """Establecer tarjeta como predeterminada"""
        tarjeta = db.query(MetodoPago).filter(
            MetodoPago.id_metodo_pago == id_tarjeta,
            MetodoPago.id_cliente == id_cliente
        ).first()

        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

        # Quitar default de todas las tarjetas del cliente
        db.query(MetodoPago).filter(MetodoPago.id_cliente == id_cliente).update({"is_default": False})

        # Establecer esta como default
        tarjeta.is_default = True
        db.commit()
        db.refresh(tarjeta)

        logger.info(f"Tarjeta {id_tarjeta} establecida como predeterminada para cliente {id_cliente}")

        # Retornar con número enmascarado
        masked_number = f"**** **** **** **{tarjeta.card_number[-2:]}" if len(tarjeta.card_number) >= 4 else "**** **** **** ****"

        return MetodoPagoResponseSchema(
            id=tarjeta.id_metodo_pago,
            id_cliente=tarjeta.id_cliente,
            cardholderName=tarjeta.cardholder_name,
            cardNumber=masked_number,
            expiryDate=tarjeta.expiry_date,
            isDefault=tarjeta.is_default,
            fecha_creacion=tarjeta.fecha_creacion,
            ultima_actualizacion=tarjeta.ultima_actualizacion
        )

