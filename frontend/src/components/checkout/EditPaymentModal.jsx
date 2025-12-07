import { useState, useEffect } from 'react'
import { Modal } from '../common/Modal'
import { PaymentFormModal } from '../account/payment/PaymentFormModal'

export function EditPaymentModal({ isOpen, onClose, onSave, initialData }) {
    const [showPaymentForm, setShowPaymentForm] = useState(false)

    const handleAddPaymentMethod = () => {
        setShowPaymentForm(true)
    }

    const handleSavePaymentMethod = (paymentData) => {
        onSave(paymentData)
        setShowPaymentForm(false)
        onClose()
    }

    return (
        <>
            <Modal isOpen={isOpen} onClose={onClose} title="MÉTODO DE PAGO">
                <div className="space-y-4">
                    {initialData ? (
                        // Mostrar método de pago actual
                        <div className="p-4 border border-gray-200 dark:border-zinc-700 rounded-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium text-gray-900 dark:text-zinc-100">
                                        {initialData.cardholderName}
                                    </p>
                                    <p className="text-sm text-gray-600 dark:text-zinc-400">
                                        {initialData.cardNumber}
                                    </p>
                                    <p className="text-sm text-gray-500 dark:text-zinc-500">
                                        Expira: {initialData.expiryDate}
                                    </p>
                                </div>
                                <button
                                    onClick={handleAddPaymentMethod}
                                    className="px-4 py-2 bg-[rgb(169,191,162)] text-white text-sm font-light hover:bg-[rgb(159,181,152)] transition-colors rounded"
                                >
                                    Cambiar
                                </button>
                            </div>
                        </div>
                    ) : (
                        // No hay método de pago
                        <div className="text-center py-8">
                            <p className="text-gray-600 dark:text-zinc-400 mb-4">
                                No tienes ningún método de pago registrado
                            </p>
                            <button
                                onClick={handleAddPaymentMethod}
                                className="px-6 py-2 bg-[rgb(169,191,162)] text-white text-sm font-light hover:bg-[rgb(159,181,152)] transition-colors rounded"
                            >
                                Añadir método de pago
                            </button>
                        </div>
                    )}
                </div>
            </Modal>

            {/* Payment Form Modal */}
            <PaymentFormModal
                isOpen={showPaymentForm}
                onClose={() => setShowPaymentForm(false)}
                onSave={handleSavePaymentMethod}
                mode="add"
                isCheckout={true}
            />
        </>
    )
}
