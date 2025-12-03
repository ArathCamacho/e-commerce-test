import { useState } from 'react'
import { AddressCard } from './address/AddressCard'
import { AddressFormModal } from './address/AddressFormModal'
import { ConfirmationModal } from '../common/ConfirmationModal'
import { useAddressManagement } from './address/useAddressManagement'
import { ADDRESS_CONTAINER_MAX_WIDTH } from '../../utils/constants'

export function ShippingAddresses() {
    // Use custom hook for address management
    const {
        addresses,
        addAddress,
        updateAddress,
        deleteAddress,
        setDefaultAddress,
        getAddressById,
        unsetDefaultAddress
    } = useAddressManagement()

    // Modal states
    const [showAddModal, setShowAddModal] = useState(false)
    const [showEditModal, setShowEditModal] = useState(false)
    const [showDeleteModal, setShowDeleteModal] = useState(false)
    const [showDefaultModal, setShowDefaultModal] = useState(false)

    // Selected items
    const [editingAddressId, setEditingAddressId] = useState(null)
    const [deletingAddressId, setDeletingAddressId] = useState(null)
    const [selectedAddressId, setSelectedAddressId] = useState(null)

    // Handlers
    const handleAddressClick = (id) => {
        const address = getAddressById(id)
        if (!address.isDefault) {
            setSelectedAddressId(id)
            setShowDefaultModal(true)
        }
    }

    const handleSetDefault = () => {
        setDefaultAddress(selectedAddressId)
        setShowDefaultModal(false)
        setSelectedAddressId(null)
    }

    const handleEdit = (address) => {
        setEditingAddressId(address.id)
        setShowEditModal(true)
    }

    const handleSaveEdit = (formData) => {
        updateAddress(editingAddressId, formData)
        setShowEditModal(false)
        setEditingAddressId(null)
    }

    const handleDelete = (id) => {
        setDeletingAddressId(id)
        setShowDeleteModal(true)
    }

    const handleConfirmDelete = () => {
        deleteAddress(deletingAddressId)
        setShowDeleteModal(false)
        setDeletingAddressId(null)
    }

    const handleAddAddress = () => {
        setShowAddModal(true)
    }

    const handleSaveNewAddress = (formData) => {
        addAddress(formData)
        setShowAddModal(false)
    }

    const handleRemoveDefault = (addressId) => {
        unsetDefaultAddress()
    }

    const editingAddress = editingAddressId ? getAddressById(editingAddressId) : null

    return (
        <div className="w-full" style={{ maxWidth: ADDRESS_CONTAINER_MAX_WIDTH }}>
            {/* Header */}
            <h2 className="text-lg font-bold text-[rgb(77,76,76)] dark:text-zinc-100 mb-4">
                Domicilios de envío
            </h2>

            {/* Add Button */}
            <button
                onClick={handleAddAddress}
                className="mb-6 px-6 py-1.5 bg-[rgb(169,191,162)] text-white text-sm font-light hover:bg-[rgb(159,181,152)] transition-colors"
            >
                Añadir nueva dirección
            </button>

            {/* Address Cards Grid */}
            <div className="flex gap-6 flex-wrap">
                {addresses.map((address) => (
                    <AddressCard
                        key={address.id}
                        address={address}
                        onClick={handleAddressClick}
                        onEdit={handleEdit}
                        onDelete={handleDelete}
                        onRemoveDefault={handleRemoveDefault}
                    />
                ))}
            </div>

            {/* Modals */}
            <AddressFormModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
                onSave={handleSaveNewAddress}
                mode="add"
            />

            <AddressFormModal
                isOpen={showEditModal}
                onClose={() => {
                    setShowEditModal(false)
                    setEditingAddressId(null)
                }}
                onSave={handleSaveEdit}
                address={editingAddress}
                mode="edit"
            />

            <ConfirmationModal
                isOpen={showDefaultModal}
                onClose={() => {
                    setShowDefaultModal(false)
                    setSelectedAddressId(null)
                }}
                onConfirm={handleSetDefault}
                title="Dirección predeterminada"
                message="¿Deseas establecer esta dirección como predeterminada?"
                confirmText="Confirmar"
                confirmStyle="primary"
            />

            <ConfirmationModal
                isOpen={showDeleteModal}
                onClose={() => {
                    setShowDeleteModal(false)
                    setDeletingAddressId(null)
                }}
                onConfirm={handleConfirmDelete}
                title="Eliminar dirección"
                message="¿Estás seguro de que deseas eliminar esta dirección?"
                confirmText="Eliminar"
                confirmStyle="danger"
            />
        </div>
    )
}
