import { useState, useEffect } from 'react'
import { Modal } from '../../common/Modal'
import { FormInput } from '../../common/FormInput'
import { validatePaymentCard, hasErrors } from '../../../utils/validation'
import { PLACEHOLDERS } from '../../../utils/constants'

/**
 * Payment Form Modal
 * Unified modal for adding and editing payment methods
 */
export function PaymentFormModal({ isOpen, onClose, onSave, card, mode = 'add' }) {
    const [formData, setFormData] = useState({
        cardholderName: '',
        cardNumber: '',
        expiryDate: '',
        cvv: ''
    })
    const [errors, setErrors] = useState({})

    // Initialize form data when modal opens or card changes
    useEffect(() => {
        if (isOpen) {
            if (mode === 'edit' && card) {
                setFormData({
                    cardholderName: card.cardholderName || '',
                    cardNumber: card.cardNumber || '',
                    expiryDate: card.expiryDate || '',
                    cvv: card.cvv || ''
                })
            } else {
                setFormData({
                    cardholderName: '',
                    cardNumber: '',
                    expiryDate: '',
                    cvv: ''
                })
            }
            setErrors({})
        }
    }, [isOpen, card, mode])

    const handleChange = (field, value) => {
        let formattedValue = value

        // Format card number with spaces
        if (field === 'cardNumber') {
            formattedValue = value.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim()
        }

        // Format expiry date with slash
        if (field === 'expiryDate') {
            formattedValue = value.replace(/\D/g, '')
            if (formattedValue.length >= 2) {
                formattedValue = formattedValue.slice(0, 2) + '/' + formattedValue.slice(2, 4)
            }
        }

        // Limit CVV to 4 digits
        if (field === 'cvv') {
            formattedValue = value.replace(/\D/g, '').slice(0, 4)
        }

        setFormData(prev => ({ ...prev, [field]: formattedValue }))

        // Clear error for this field when user starts typing
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: null }))
        }
    }

    const handleSubmit = () => {
        const validationErrors = validatePaymentCard(formData)

        if (hasErrors(validationErrors)) {
            setErrors(validationErrors)
            return
        }

        onSave(formData)
        onClose()
    }

    const title = mode === 'add' ? 'Añadir nueva tarjeta' : 'Editar tarjeta'

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={title}>
            <div className="space-y-4 mb-8">
                <FormInput
                    label="Nombre del titular"
                    value={formData.cardholderName}
                    onChange={(e) => handleChange('cardholderName', e.target.value)}
                    error={errors.cardholderName}
                    placeholder={PLACEHOLDERS.cardholderName}
                />

                <FormInput
                    label="Número de tarjeta"
                    value={formData.cardNumber}
                    onChange={(e) => handleChange('cardNumber', e.target.value)}
                    error={errors.cardNumber}
                    placeholder={PLACEHOLDERS.cardNumber}
                    maxLength={19}
                />

                <div className="grid grid-cols-2 gap-4">
                    <FormInput
                        label="Fecha de expiración"
                        value={formData.expiryDate}
                        onChange={(e) => handleChange('expiryDate', e.target.value)}
                        error={errors.expiryDate}
                        placeholder={PLACEHOLDERS.expiryDate}
                        maxLength={5}
                    />

                    <FormInput
                        label="CVV"
                        type="password"
                        value={formData.cvv}
                        onChange={(e) => handleChange('cvv', e.target.value)}
                        error={errors.cvv}
                        placeholder={PLACEHOLDERS.cvv}
                        maxLength={4}
                    />
                </div>
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
