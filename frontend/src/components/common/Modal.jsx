import { X } from 'lucide-react'

/**
 * Reusable Modal Component
 * @param {boolean} isOpen - Controls modal visibility
 * @param {function} onClose - Callback when modal should close
 * @param {string} title - Modal title
 * @param {ReactNode} children - Modal content
 * @param {string} width - Custom width (default: '500px')
 */
export function Modal({ isOpen, onClose, title, children, width = '500px' }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50">
            <div
                className="bg-white dark:bg-zinc-900 p-8 max-h-[90vh] overflow-y-auto"
                style={{ width }}
            >
                {/* Header */}
                <div className="flex justify-between items-start mb-6">
                    <h3 className="text-lg font-normal text-black dark:text-zinc-100">
                        {title}
                    </h3>
                    <button
                        onClick={onClose}
                        className="text-black dark:text-zinc-100 hover:text-gray-600 dark:hover:text-zinc-400 transition-colors"
                        aria-label="Cerrar modal"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                {children}
            </div>
        </div>
    )
}
