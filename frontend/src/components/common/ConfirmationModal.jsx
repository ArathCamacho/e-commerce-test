import { Modal } from './Modal'

/**
 * Reusable Confirmation Modal
 * @param {boolean} isOpen - Controls modal visibility
 * @param {function} onClose - Callback when modal should close
 * @param {function} onConfirm - Callback when user confirms
 * @param {string} title - Modal title
 * @param {string} message - Confirmation message
 * @param {string} confirmText - Confirm button text (default: 'Confirmar')
 * @param {string} cancelText - Cancel button text (default: 'Cancelar')
 * @param {string} confirmStyle - Confirm button style variant ('primary' | 'danger')
 */
export function ConfirmationModal({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    confirmText = 'Confirmar',
    cancelText = 'Cancelar',
    confirmStyle = 'primary'
}) {
    const confirmButtonClass = confirmStyle === 'danger'
        ? 'bg-red-500 text-white hover:bg-red-600'
        : 'bg-[rgb(169,191,162)] text-white hover:bg-[rgb(159,181,152)]'

    return (
        <Modal isOpen={isOpen} onClose={onClose} title={title} width="400px">
            <p className="text-base font-light text-[rgb(77,76,76)] dark:text-zinc-400 mb-8">
                {message}
            </p>

            <div className="flex gap-4">
                <button
                    onClick={onClose}
                    className="flex-1 h-[35px] border border-black dark:border-zinc-400 text-black dark:text-zinc-100 text-base font-light hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
                >
                    {cancelText}
                </button>
                <button
                    onClick={onConfirm}
                    className={`flex-1 h-[35px] text-base font-light transition-colors ${confirmButtonClass}`}
                >
                    {confirmText}
                </button>
            </div>
        </Modal>
    )
}
