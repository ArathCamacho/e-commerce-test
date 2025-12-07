import { useState } from 'react'
import { EditInfoModal } from './EditInfoModal'
import { EditAddressModal } from './EditAddressModal'
import { EditPaymentModal } from './EditPaymentModal'
import { useCheckout } from '../../context/CheckoutContext'

export function CheckoutInfo() {
    const {
        userInfo,
        address,
        paymentMethod,
        updateUserInfo,
        updateAddress,
        savePaymentMethod,
        showAddressModal,
        showPaymentModal,
        openAddressModal,
        closeAddressModal,
        openPaymentModal,
        closePaymentModal
    } = useCheckout()

    const [infoModalOpen, setInfoModalOpen] = useState(false)

    // Función para enmascarar número de tarjeta
    const maskCardNumber = (cardNumber) => {
        if (!cardNumber) return ''
        // Mantener solo los últimos 4 dígitos
        const lastFour = cardNumber.slice(-4)
        return `**** **** **** ${lastFour}`
    }

    return (
        <>
            <div className="space-y-8">
                {/* MI INFORMACIÓN */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            MI INFORMACIÓN
                        </h2>
                        <button
                            onClick={() => setInfoModalOpen(true)}
                            className="text-sm text-gray-600 dark:text-zinc-400 underline hover:text-gray-900 dark:hover:text-zinc-100 uppercase transition-colors"
                        >
                            EDITAR
                        </button>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-1">
                        <p className="font-medium">{userInfo.name}</p>
                        <p>{userInfo.email}</p>
                        <p>{userInfo.phone || 'Teléfono no registrado'}</p>
                    </div>
                </div>

                {/* DIRECCIÓN DE FACTURACIÓN */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            DIRECCIÓN DE ENVÍO
                        </h2>
                        <button
                            onClick={openAddressModal}
                            className="text-sm text-gray-600 dark:text-zinc-400 underline hover:text-gray-900 dark:hover:text-zinc-100 uppercase transition-colors"
                        >
                            EDITAR
                        </button>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-1">
                        <p>{address.street}</p>
                        <p>{address.zipCode} {address.city}</p>
                        <p>{address.state && `${address.state}, `}{address.country}</p>
                    </div>
                </div>

                {/* MÉTODO DE PAGO */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            MÉTODO DE PAGO
                        </h2>
                        <button
                            onClick={openPaymentModal}
                            className="text-sm text-gray-600 dark:text-zinc-400 underline hover:text-gray-900 dark:hover:text-zinc-100 uppercase transition-colors"
                        >
                            EDITAR
                        </button>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-1">
                        {paymentMethod ? (
                            <>
                                <p className="font-medium">{paymentMethod.cardholderName}</p>
                                <p>{maskCardNumber(paymentMethod.cardNumber)}</p>
                                <p className="text-xs text-gray-500 dark:text-zinc-500">
                                    {paymentMethod.expiryDate}
                                </p>
                            </>
                        ) : (
                            <p className="text-gray-500 dark:text-zinc-500 italic">
                                No hay método de pago registrado
                            </p>
                        )}
                    </div>
                </div>

            </div>

            {/* Modals */}
            <EditInfoModal
                isOpen={infoModalOpen}
                onClose={() => setInfoModalOpen(false)}
                onSave={updateUserInfo}
                initialData={userInfo}
            />

            <EditAddressModal
                isOpen={showAddressModal}
                onClose={closeAddressModal}
                onSave={updateAddress}
                initialData={address}
            />

            <EditPaymentModal
                isOpen={showPaymentModal}
                onClose={closePaymentModal}
                onSave={savePaymentMethod}
                initialData={paymentMethod}
            />

        </>
    )
}