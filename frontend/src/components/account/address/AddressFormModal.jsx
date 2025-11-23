import { useState, useEffect } from 'react'
import { Modal } from '../../common/Modal'
import { FormInput } from '../../common/FormInput'
import { validateAddress, hasErrors } from '../../../utils/validation'
import { PLACEHOLDERS, POSTAL_CODE_LENGTH } from '../../../utils/constants'

/**
 * Address Form Modal
 * Unified modal for adding and editing addresses
 */
export function AddressFormModal({ isOpen, onClose, onSave, address, mode = 'add' }) {
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        street: '',
        details: '',
        city: '',
        postalCode: ''
    })
    const [errors, setErrors] = useState({})

    // Initialize form data when modal opens or address changes
    useEffect(() => {
        if (isOpen) {
            if (mode === 'edit' && address) {
                setFormData({
                    name: address.name || '',
                    phone: address.phone || '',
                    street: address.street || '',
                    details: address.details || '',
                    city: address.city || '',
                    postalCode: address.postalCode || ''
                })
            } else {
                setFormData({
                    name: '',
                    phone: '',
                    street: '',
                    details: '',
                    city: '',
                    postalCode: ''
                })
            }
            setErrors({})
        }
    }, [isOpen, address, mode])

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }))
        // Clear error for this field when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: null }))
        }
    }

    const handleSubmit = () => {
        const validationErrors = validateAddress(formData)

        if (hasErrors(validationErrors)) {
            setErrors(validationErrors)
            return
        }

        onSave(formData)
        onClose()
    }

    const title = mode === 'add' ? 'Añadir nueva dirección' : 'Editar dirección'

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={title}>
            <div className="space-y-4 mb-8">
                <FormInput
                    label="Nombre"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    error={errors.name}
                    placeholder={PLACEHOLDERS.name}
                />

                <FormInput
                    label="Teléfono"
                    value={formData.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    error={errors.phone}
                    placeholder={PLACEHOLDERS.phone}
                />

                <FormInput
                    label="Calle"
                    value={formData.street}
                    onChange={(e) => handleChange('street', e.target.value)}
                    error={errors.street}
                    placeholder={PLACEHOLDERS.street}
                />

                <FormInput
                    label="Detalles"
                    value={formData.details}
                    onChange={(e) => handleChange('details', e.target.value)}
                    error={errors.details}
                    placeholder={PLACEHOLDERS.details}
                />

                <FormInput
                    label="Ciudad"
                    value={formData.city}
                    onChange={(e) => handleChange('city', e.target.value)}
                    error={errors.city}
                    placeholder={PLACEHOLDERS.city}
                />

                <FormInput
                    label="Código Postal"
                    value={formData.postalCode}
                    onChange={(e) => handleChange('postalCode', e.target.value)}
                    error={errors.postalCode}
                    placeholder={PLACEHOLDERS.postalCode}
                    maxLength={POSTAL_CODE_LENGTH}
                />
            </div>

            <div className="flex gap-4">
                <button
                    onClick={onClose}
                    className="flex-1 h-[35px] border border-black dark:border-zinc-400 text-black dark:text-zinc-100 text-base font-light hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
                >
                    Cancelar
                </button>
                <button
                    onClick={handleSubmit}
                    className="flex-1 h-[35px] bg-[rgb(169,191,162)] text-white text-base font-light hover:bg-[rgb(159,181,152)] transition-colors"
                >
                    Guardar
                </button>
            </div>
        </Modal>
    )
}
