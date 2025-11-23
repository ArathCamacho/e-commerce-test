import { useCart } from '../context/CartContext'
import { Check, X, AlertCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

export function Notification() {
    const { notification } = useCart()
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        if (notification.show) {
            setIsVisible(true)
        } else {
            // Esperar a que termine la animación de salida antes de desmontar completamente si fuera necesario
            // pero aquí controlamos la visibilidad con clases
            const timer = setTimeout(() => setIsVisible(false), 300)
            return () => clearTimeout(timer)
        }
    }, [notification.show])

    if (!notification.show && !isVisible) return null

    const isSuccess = notification.type === 'success'

    return (
        <div
            className={`fixed top-24 right-4 z-50 transition-all duration-300 transform ${notification.show
                    ? 'translate-x-0 opacity-100'
                    : 'translate-x-full opacity-0'
                }`}
        >
            <div className={`flex items-center gap-3 px-6 py-4 shadow-lg border-l-4 ${isSuccess
                    ? 'bg-white dark:bg-zinc-800 border-green-500'
                    : 'bg-white dark:bg-zinc-800 border-red-500'
                }`}>
                <div className={`rounded-full p-1 ${isSuccess ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                    }`}>
                    {isSuccess ? <Check className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                </div>

                <div>
                    <h4 className={`font-bold text-sm ${isSuccess ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {isSuccess ? '¡Éxito!' : 'Atención'}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-zinc-300">
                        {notification.message}
                    </p>
                </div>

                <button className="text-gray-400 hover:text-gray-600 dark:hover:text-zinc-200 ml-2">
                    <X className="w-4 h-4" />
                </button>
            </div>
        </div>
    )
}
