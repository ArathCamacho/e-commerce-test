import { User, MapPin } from 'lucide-react'
import { ADDRESS_CARD_WIDTH, ADDRESS_CARD_MIN_HEIGHT } from '../../../utils/constants'

/**
 * Address Card Component
 * Displays a single address with actions
 */
export function AddressCard({ address, onEdit, onDelete, onClick }) {
    return (
        <fieldset
            onClick={() => onClick(address.id)}
            className={`p-5 relative cursor-pointer transition-all w-full sm:w-auto ${address.isDefault
                ? 'bg-[rgb(240,244,239)] dark:bg-zinc-800 border border-[rgb(169,191,162)] dark:border-[rgb(169,191,162)]'
                : 'bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700'
                }`}
            style={{ width: 'auto', maxWidth: '100%', minWidth: '252px', minHeight: ADDRESS_CARD_MIN_HEIGHT }}
        >
            {/* Default Label */}
            {address.isDefault && (
                <legend className="px-2 text-xs font-light text-[rgb(169,191,162)] mx-auto">
                    Dirección predeterminada
                </legend>
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
