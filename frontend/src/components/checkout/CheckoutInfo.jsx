import { useState } from 'react'
import { EditInfoModal } from './EditInfoModal'
import { EditAddressModal } from './EditAddressModal'
import { EditShippingModal } from './EditShippingModal'

export function CheckoutInfo() {
    const [infoModalOpen, setInfoModalOpen] = useState(false)
    const [addressModalOpen, setAddressModalOpen] = useState(false)
    const [shippingModalOpen, setShippingModalOpen] = useState(false)

    const [userInfo, setUserInfo] = useState({
        name: 'Sebastián Sotelo Rodríguez',
        email: 'sebastian05@gmail.com'
    })

    const [address, setAddress] = useState({
        street: 'Calle Siempre viva #54',
        zipCode: '83125',
        city: 'Hermosillo',
        country: 'México'
    })

    const [shipping, setShipping] = useState({
        name: 'Sebastián Sotelo Rodríguez',
        phone: '+52 662 154 5465'
    })

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
                    </div>
                </div>

                {/* DIRECCIÓN DE FACTURACIÓN */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            DIRECCIÓN DE FACTURACIÓN
                        </h2>
                        <button
                            onClick={() => setAddressModalOpen(true)}
                            className="text-sm text-gray-600 dark:text-zinc-400 underline hover:text-gray-900 dark:hover:text-zinc-100 uppercase transition-colors"
                        >
                            EDITAR
                        </button>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-1">
                        <p>{address.street}</p>
                        <p>{address.zipCode} {address.city}</p>
                        <p>{address.country}</p>
                    </div>
                </div>

                {/* ENVÍO */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            ENVÍO
                        </h2>
                        <button
                            onClick={() => setShippingModalOpen(true)}
                            className="text-sm text-gray-600 dark:text-zinc-400 underline hover:text-gray-900 dark:hover:text-zinc-100 uppercase transition-colors"
                        >
                            EDITAR
                        </button>
                    </div>
                    <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-1">
                        <p className="font-medium">{shipping.name}</p>
                        <p>{shipping.phone}</p>
                    </div>
                </div>
            </div>

            {/* Modals */}
            <EditInfoModal
                isOpen={infoModalOpen}
                onClose={() => setInfoModalOpen(false)}
                onSave={setUserInfo}
                initialData={userInfo}
            />

            <EditAddressModal
                isOpen={addressModalOpen}
                onClose={() => setAddressModalOpen(false)}
                onSave={setAddress}
                initialData={address}
            />

            <EditShippingModal
                isOpen={shippingModalOpen}
                onClose={() => setShippingModalOpen(false)}
                onSave={setShipping}
                initialData={shipping}
            />
        </>
    )
}
