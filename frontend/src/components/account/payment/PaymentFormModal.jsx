import { useState, useEffect } from 'react'
import { Modal } from '../../common/Modal'
import { FormInput } from '../../common/FormInput'
import { validatePaymentCard, hasErrors } from '../../../utils/validation'
import { PLACEHOLDERS } from '../../../utils/constants'

/**
 * Payment Form Modal
 * Unified modal for adding and editing payment methods
 */
export function PaymentFormModal({ isOpen, onClose, onSave, card, mode = 'add', isCheckout = false }) {
    const [formData, setFormData] = useState({
        cardholderName: '',
        cardNumber: '',
        expiryDate: '',
        cvv: ''
    })
    const [errors, setErrors] = useState({})
    const [paymentPreference, setPaymentPreference] = useState('default') // 'default' or 'oneTime'

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
                // Auto-fill with default test data for new cards
                setFormData({
                    cardholderName: 'Arath Camacho VPV',
                    cardNumber: '4111 1111 1115',
                    expiryDate: '12/30',
                    cvv: '567'
                })
            }
            setErrors({})
            setPaymentPreference('default') // Reset to default (already selected)
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

        // Include payment preference in the returned data if in checkout mode
        const dataToSave = isCheckout
            ? { ...formData, isDefault: paymentPreference === 'default', isOneTime: paymentPreference === 'oneTime' }
            : formData

        onSave(dataToSave)
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

                {/* Checkout Mode: Payment Preference */}
                {isCheckout && (
                    <div className="mt-6 pt-6 border-t border-gray-200 dark:border-zinc-700">
                        <p className="text-sm font-medium text-gray-700 dark:text-zinc-300 mb-4">
                            ¿Desea que este sea su método de pago predeterminado?
                        </p>
                        <div className="space-y-3">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <input
                                    type="radio"
                                    name="paymentPreference"
                                    value="default"
                                    checked={paymentPreference === 'default'}
                                    onChange={() => setPaymentPreference('default')}
                                    className="sr-only"
                                />
                                <div className={`w-5 h-5 border rounded-full flex items-center justify-center transition-colors ${paymentPreference === 'default'
                                    ? 'border-[rgb(169,191,162)]'
                                    : 'border-gray-300 dark:border-zinc-600'
                                    }`}>
                                    {paymentPreference === 'default' && (
                                        <div className="w-3 h-3 bg-[rgb(169,191,162)] rounded-full" />
                                    )}
                                </div>
                                <span className="text-sm text-gray-700 dark:text-zinc-300 group-hover:text-gray-900 dark:group-hover:text-zinc-100">
                                    Establecer como predeterminado
                                </span>
                            </label>
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <input
                                    type="radio"
                                    name="paymentPreference"
                                    value="oneTime"
                                    checked={paymentPreference === 'oneTime'}
                                    onChange={() => setPaymentPreference('oneTime')}
                                    className="sr-only"
                                />
                                <div className={`w-5 h-5 border rounded-full flex items-center justify-center transition-colors ${paymentPreference === 'oneTime'
                                    ? 'border-[rgb(169,191,162)]'
                                    : 'border-gray-300 dark:border-zinc-600'
                                    }`}>
                                    {paymentPreference === 'oneTime' && (
                                        <div className="w-3 h-3 bg-[rgb(169,191,162)] rounded-full" />
                                    )}
                                </div>
                                <span className="text-sm text-gray-700 dark:text-zinc-300 group-hover:text-gray-900 dark:group-hover:text-zinc-100">
                                    Única vez
                                </span>
                            </label>
                        </div>
                    </div>
                )}
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
