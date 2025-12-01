import { User, CreditCard, X } from 'lucide-react'
import { useState } from 'react'

/**
 * Payment Card Component
 * Displays a single payment method with actions
 */
export function PaymentCard({ card, onEdit, onDelete, onClick, onRemoveDefault }) {
    const [isHovering, setIsHovering] = useState(false)

    // Mask card number showing only last 4 digits
    const maskedNumber = `**** **** **** **${card.cardNumber.slice(-2)}`

    const handleRemoveDefault = (e) => {
        e.stopPropagation()
        if (onRemoveDefault) {
            onRemoveDefault(card.id)
        }
    }

    return (
        <fieldset
            onClick={() => onClick(card.id)}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}
            className={`p-5 relative cursor-pointer transition-all w-full sm:w-72 aspect-square ${card.isDefault
                ? 'bg-[rgb(240,244,239)] dark:bg-zinc-800 border border-[rgb(169,191,162)] dark:border-[rgb(169,191,162)]'
                : 'bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700'
                }`}
        >
            {/* Default Label */}
            {card.isDefault && (
                <legend className="px-2 text-xs font-light text-[rgb(169,191,162)] mx-auto">
                    Tarjeta predeterminada
                </legend>
            )}

            {/* Remove Default Button - Appears on Hover */}
            {card.isDefault && isHovering && onRemoveDefault && (
                <button
                    onClick={handleRemoveDefault}
                    className={`absolute top-3 right-3 w-6 h-6 bg-[rgb(169,191,162)] hover:bg-[rgb(159,181,152)] text-white rounded-full flex items-center justify-center transition-all duration-300 z-10 border-2 border-white ${isHovering ? 'scale-100 opacity-100' : 'scale-0 opacity-0'
                        }`}
                >
                    <X className="w-3.5 h-3.5" />
                </button>
            )}

            {/* Content */}
            <div className="space-y-4 pb-12">
                {/* Cardholder Name */}
                <div className="flex items-start gap-2">
                    <User className="w-4 h-4 text-black dark:text-zinc-100 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-light text-black dark:text-zinc-100">
                            {card.cardholderName}
                        </p>
                    </div>
                </div>

                {/* Card Number */}
                <div className="flex items-start gap-2">
                    <CreditCard className="w-4 h-4 text-black dark:text-zinc-100 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-light text-black dark:text-zinc-100">
                            {maskedNumber}
                        </p>
                    </div>
                </div>

                {/* Helper Text */}
                <div className="mt-8">
                    <p className="text-xs font-light text-gray-500 dark:text-zinc-500 text-center">
                        Seleccione editar para ver mas detalle o elimine la tarjeta.
                    </p>
                </div>
            </div>

            {/* Actions at bottom */}
            <div className="absolute bottom-5 left-5 right-5 flex gap-4 pt-4 border-t border-gray-200 dark:border-zinc-700">
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        onEdit(card)
                    }}
                    className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                >
                    Editar
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        onDelete(card.id)
                    }}
                    className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                >
                    Eliminar
                </button>
            </div>
        </fieldset>
    )
}
