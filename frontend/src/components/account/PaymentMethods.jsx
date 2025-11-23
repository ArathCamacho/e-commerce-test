import { useState } from 'react'
import { PaymentCard } from './payment/PaymentCard'
import { PaymentFormModal } from './payment/PaymentFormModal'
import { ConfirmationModal } from '../common/ConfirmationModal'
import { usePaymentManagement } from './payment/usePaymentManagement'
import { ADDRESS_CONTAINER_MAX_WIDTH } from '../../utils/constants'

// Initial sample data
const INITIAL_CARDS = [
    {
        id: 1,
        cardholderName: 'Sebastian',
        cardNumber: '4532123456789093',
        expiryDate: '12/25',
        cvv: '123',
        isDefault: true
    },
    {
        id: 2,
        cardholderName: 'Arath',
        cardNumber: '5425233430109032',
        expiryDate: '06/26',
        cvv: '456',
        isDefault: false
    }
]

export function PaymentMethods() {
    // Use custom hook for payment management
    const {
        cards,
        addCard,
        updateCard,
        deleteCard,
        setDefaultCard,
        getCardById
    } = usePaymentManagement(INITIAL_CARDS)

    // Modal states
    const [showAddModal, setShowAddModal] = useState(false)
    const [showEditModal, setShowEditModal] = useState(false)
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [showDefaultModal, setShowDefaultModal] = useState(false)

    // Selected items
    const [editingCardId, setEditingCardId] = useState(null)
    const [deletingCardId, setDeletingCardId] = useState(null)
    const [selectedCardId, setSelectedCardId] = useState(null)

    // Handlers
    const handleCardClick = (id) => {
        const card = getCardById(id)
        if (!card.isDefault) {
            setSelectedCardId(id)
            setShowDefaultModal(true)
        }
    }

    const handleSetDefault = () => {
        setDefaultCard(selectedCardId)
        setShowDefaultModal(false)
        setSelectedCardId(null)
    }

    const handleEdit = (card) => {
        setEditingCardId(card.id)
        setShowEditModal(true)
    }

    const handleSaveEdit = (formData) => {
        updateCard(editingCardId, formData)
        setShowEditModal(false)
        setEditingCardId(null)
    }

    const handleDelete = (id) => {
        setDeletingCardId(id)
        setShowDeleteModal(true)
    }

    const handleConfirmDelete = () => {
        deleteCard(deletingCardId)
        setShowDeleteModal(false)
        setDeletingCardId(null)
    }

    const handleAddCard = () => {
        setShowAddModal(true)
    }

    const handleSaveNewCard = (formData) => {
        addCard(formData)
        setShowAddModal(false)
    }

    const editingCard = editingCardId ? getCardById(editingCardId) : null

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
                {cards.map((card) => (
                    <PaymentCard
                        key={card.id}
                        card={card}
                        onClick={handleCardClick}
                        onEdit={handleEdit}
                        onDelete={handleDelete}
                    />
                ))}
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
