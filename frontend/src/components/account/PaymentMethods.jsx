import { useState, useEffect } from 'react'
import { PaymentCard } from './payment/PaymentCard'
import { PaymentFormModal } from './payment/PaymentFormModal'
import { ConfirmationModal } from '../common/ConfirmationModal'
import { MetodoPagoService } from '../../services/apiservice'
import { obtenerClienteLocal } from '../../services/apiservice'
import { ADDRESS_CONTAINER_MAX_WIDTH } from '../../utils/constants'

export function PaymentMethods() {
    const [cards, setCards] = useState([])
    const [loading, setLoading] = useState(true)
    const [cliente, setCliente] = useState(null)

    // Modal states
    const [showAddModal, setShowAddModal] = useState(false)
    const [showEditModal, setShowEditModal] = useState(false)
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [showDefaultModal, setShowDefaultModal] = useState(false)

    // Selected items
    const [editingCardId, setEditingCardId] = useState(null)
    const [deletingCardId, setDeletingCardId] = useState(null)
    const [selectedCardId, setSelectedCardId] = useState(null)

    // Cargar tarjetas del backend
    useEffect(() => {
        const loadCards = async () => {
            try {
                const clienteData = obtenerClienteLocal()
                if (clienteData?.id_cliente) {
                    setCliente(clienteData)
                    const tarjetas = await MetodoPagoService.obtenerTarjetas(clienteData.id_cliente)

                    // Convertir formato del backend al formato esperado por el frontend
                    const formattedCards = (tarjetas || []).map(tarjeta => ({
                        id: tarjeta.id,
                        cardholderName: tarjeta.cardholderName,
                        cardNumber: tarjeta.cardNumber,
                        expiryDate: tarjeta.expiryDate,
                        cvv: '', // No se retorna por seguridad
                        isDefault: tarjeta.isDefault
                    }))

                    setCards(formattedCards)
                }
            } catch (error) {
                console.error('Error loading cards:', error)
                setCards([])
            } finally {
                setLoading(false)
            }
        }

        loadCards()
    }, [])

    // Funciones para gestionar tarjetas
    const getCardById = (id) => cards.find(card => card.id === id)

    // Función para convertir datos del formulario al formato del backend
    const convertFormData = (formData) => ({
        cardholderName: formData.cardholderName,
        cardNumber: formData.cardNumber,
        expiryDate: formData.expiryDate,
        cvv: formData.cvv,
        isDefault: formData.isDefault || false
    })

    const addCard = async (formData) => {
        try {
            const newCard = await MetodoPagoService.agregarTarjeta(cliente.id_cliente, formData)
            // Convertir formato del backend
            const formattedCard = {
                id: newCard.id,
                cardholderName: newCard.cardholderName,
                cardNumber: newCard.cardNumber,
                expiryDate: newCard.expiryDate,
                cvv: '',
                isDefault: newCard.isDefault
            }
            setCards(prev => [...prev, formattedCard])
        } catch (error) {
            console.error('Error adding card:', error)
            throw error
        }
    }

    const updateCard = async (id, formData) => {
        try {
            const updatedCard = await MetodoPagoService.actualizarTarjeta(cliente.id_cliente, id, formData)
            // Convertir formato del backend
            const formattedCard = {
                id: updatedCard.id,
                cardholderName: updatedCard.cardholderName,
                cardNumber: updatedCard.cardNumber,
                expiryDate: updatedCard.expiryDate,
                cvv: '',
                isDefault: updatedCard.isDefault
            }
            setCards(prev => prev.map(card => card.id === id ? formattedCard : card))
        } catch (error) {
            console.error('Error updating card:', error)
            throw error
        }
    }

    const deleteCard = async (id) => {
        try {
            await MetodoPagoService.eliminarTarjeta(cliente.id_cliente, id)
            setCards(prev => prev.filter(card => card.id !== id))
        } catch (error) {
            console.error('Error deleting card:', error)
            throw error
        }
    }

    const setDefaultCard = async (id) => {
        try {
            await MetodoPagoService.establecerPredeterminada(cliente.id_cliente, id)
            setCards(prev => prev.map(card => ({
                ...card,
                isDefault: card.id === id
            })))
        } catch (error) {
            console.error('Error setting default card:', error)
            throw error
        }
    }

    const unsetDefaultCard = async () => {
        try {
            // Aquí podrías llamar a una API para quitar la tarjeta predeterminada
            setCards(prev => prev.map(card => ({
                ...card,
                isDefault: false
            })))
        } catch (error) {
            console.error('Error unsetting default card:', error)
        }
    }

    // Handlers
    const handleCardClick = (id) => {
        const card = getCardById(id)
        if (!card.isDefault) {
            setSelectedCardId(id)
            setShowDefaultModal(true)
        }
    }

    const handleSetDefault = async () => {
        try {
            await setDefaultCard(selectedCardId)
            setShowDefaultModal(false)
            setSelectedCardId(null)
        } catch (error) {
            console.error('Error setting default card:', error)
        }
    }

    const handleEdit = (card) => {
        setEditingCardId(card.id)
        setShowEditModal(true)
    }

    const handleSaveEdit = async (formData) => {
        try {
            await updateCard(editingCardId, convertFormData(formData))
            setShowEditModal(false)
            setEditingCardId(null)
        } catch (error) {
            console.error('Error saving edit:', error)
        }
    }

    const handleDelete = (id) => {
        setDeletingCardId(id)
        setShowDeleteModal(true)
    }

    const handleConfirmDelete = async () => {
        try {
            await deleteCard(deletingCardId)
            setShowDeleteModal(false)
            setDeletingCardId(null)
        } catch (error) {
            console.error('Error deleting card:', error)
        }
    }

    const handleAddCard = () => {
        setShowAddModal(true)
    }

    const handleSaveNewCard = async (formData) => {
        try {
            await addCard(convertFormData(formData))
            setShowAddModal(false)
        } catch (error) {
            console.error('Error saving new card:', error)
        }
    }

    const handleRemoveDefault = (cardId) => {
        unsetDefaultCard()
    }

    const editingCard = editingCardId ? getCardById(editingCardId) : null

    if (loading) {
        return (
            <div className="w-full" style={{ maxWidth: ADDRESS_CONTAINER_MAX_WIDTH }}>
                <h2 className="text-lg font-bold text-[rgb(77,76,76)] dark:text-zinc-100 mb-4">
                    Métodos de pago
                </h2>
                <div className="flex items-center justify-center py-8">
                    <div className="text-gray-500 dark:text-zinc-400">Cargando tarjetas...</div>
                </div>
            </div>
        )
    }

    return (
        <div className="w-full" style={{ maxWidth: ADDRESS_CONTAINER_MAX_WIDTH }}>
            {/* Header */}
            <h2 className="text-lg font-bold text-[rgb(77,76,76)] dark:text-zinc-100 mb-4">
                Métodos de pago
            </h2>

            {/* Add Button */}
            <button
                onClick={handleAddCard}
                className="mb-6 px-6 py-1.5 bg-[rgb(169,191,162)] text-white text-sm font-light hover:bg-[rgb(159,181,152)] transition-colors"
            >
                Añadir nueva tarjeta
            </button>

            {/* Payment Cards Grid */}
            <div className="flex gap-6 flex-wrap">
                {cards.length === 0 ? (
                    <div className="w-full text-center py-8 text-gray-500 dark:text-zinc-400">
                        No tienes tarjetas guardadas
                    </div>
                ) : (
                    cards.map((card) => (
                        <PaymentCard
                            key={card.id}
                            card={card}
                            onClick={handleCardClick}
                            onEdit={handleEdit}
                            onDelete={handleDelete}
                            onRemoveDefault={handleRemoveDefault}
                        />
                    ))
                )}
            </div>

            {/* Modals */}
            <PaymentFormModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onSave={handleSaveNewCard}
                mode="add"
            />

            <PaymentFormModal
                isOpen={showEditModal}
                onClose={() => {
                    setShowEditModal(false)
                    setEditingCardId(null)
                }}
                onSave={handleSaveEdit}
                card={editingCard}
                mode="edit"
            />

            <ConfirmationModal
                isOpen={showDefaultModal}
                onClose={() => {
                    setShowDefaultModal(false)
                    setSelectedCardId(null)
                }}
                onConfirm={handleSetDefault}
                title="Tarjeta predeterminada"
                message="¿Deseas establecer esta tarjeta como predeterminada?"
                confirmText="Confirmar"
                confirmStyle="primary"
            />

            <ConfirmationModal
                isOpen={showDeleteModal}
                onClose={() => {
                    setShowDeleteModal(false)
                    setDeletingCardId(null)
                }}
                onConfirm={handleConfirmDelete}
                title="Eliminar tarjeta"
                message="¿Estás seguro de que deseas eliminar esta tarjeta?"
                confirmText="Eliminar"
                confirmStyle="danger"
            />
        </div>
    )
}
