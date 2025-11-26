import { User, MapPin, X } from 'lucide-react'
import { useState } from 'react'

/**
 * Address Card Component
 * Displays a single address with actions
 */
export function AddressCard({ address, onEdit, onDelete, onClick, onRemoveDefault }) {
    const [isHovering, setIsHovering] = useState(false)

    const handleRemoveDefault = (e) => {
        e.stopPropagation()
        if (onRemoveDefault) {
            onRemoveDefault(address.id)
        }
    }

    return (
        <fieldset
            onClick={() => onClick(address.id)}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={() => setIsHovering(false)}
            className={`p-5 relative cursor-pointer transition-all w-full sm:w-72 aspect-square ${address.isDefault
                ? 'bg-[rgb(240,244,239)] dark:bg-zinc-800 border border-[rgb(169,191,162)] dark:border-[rgb(169,191,162)]'
                : 'bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700'
                }`}
        >
            {/* Default Label */}
            {address.isDefault && (
                <legend className="px-2 text-xs font-light text-[rgb(169,191,162)] mx-auto">
                    Dirección predeterminada
                </legend>
            )}

            {/* Remove Default Button - Appears on Hover */}
            {address.isDefault && isHovering && onRemoveDefault && (
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
                {/* Name and Phone */}
                <div className="flex items-start gap-2">
                    <User className="w-4 h-4 text-black dark:text-zinc-100 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-light text-black dark:text-zinc-100">
                            {address.name}, {address.phone}
                        </p>
                    </div>
                </div>

                {/* Address */}
                <div className="flex items-start gap-2">
                    <MapPin className="w-4 h-4 text-black dark:text-zinc-100 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-light text-black dark:text-zinc-100">
                            {address.street}
                        </p>
                        <p className="text-sm font-light text-black dark:text-zinc-100 mt-1">
                            {address.details}
                        </p>
                        <p className="text-sm font-light text-black dark:text-zinc-100 mt-1">
                            {address.city}, {address.postalCode}
                        </p>
                    </div>
                </div>
            </div>

            {/* Actions at bottom */}
            <div className="absolute bottom-5 left-5 right-5 flex gap-4 pt-4 border-t border-gray-200 dark:border-zinc-700">
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        onEdit(address)
                    }}
                    className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                >
                    Editar
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation()
                        onDelete(address.id)
                    }}
                    className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                >
                    Eliminar
                </button>
            </div>
        </fieldset>
    )
}
