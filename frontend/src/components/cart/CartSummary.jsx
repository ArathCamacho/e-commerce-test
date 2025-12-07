import { useCart } from '../../context/CartContext'
import { useNavigate } from 'react-router-dom'
import { obtenerClienteLocal } from '../../services/apiservice'

export function CartSummary() {
    const { cartTotal, cartItems } = useCart()
    const navigate = useNavigate()
    const isEmpty = cartItems.length === 0
    // const shippingCost = isEmpty ? 0 : 140.00
    const total = cartTotal // Envío gratis

    // Verificar si hay usuario logueado
    const cliente = obtenerClienteLocal()
    const isLoggedIn = cliente?.id_cliente && cliente?.nombre

    return (
        <div className="lg:sticky lg:top-24 h-fit">
            {/* Discounts Section */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                        DESCUENTOS
                    </h2>
                    <button className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase hover:text-gray-600 dark:hover:text-zinc-400 transition-colors">
                        AGREGAR
                    </button>
                </div>
            </div>

            {/* Order Summary */}
            <div className="space-y-3 mb-6 text-sm">
                <div className="flex justify-between text-gray-700 dark:text-zinc-300">
                    <span>Valor del pedido</span>
                    <span>${cartTotal.toFixed(2)}</span>
                </div>
                {/* Envío gratis */}
                {/* <div className="flex justify-between text-gray-700 dark:text-zinc-300">
                    <span>Costo estimado de envío</span>
                    <span>${shippingCost.toFixed(2)}</span>
                </div> */}
            </div>

            {/* Total */}
            <div className="flex justify-between text-base font-bold text-gray-900 dark:text-zinc-100 mb-6 pb-6 border-b border-gray-200 dark:border-zinc-800">
                <span>TOTAL</span>
                <span>${total.toFixed(2)}</span>
            </div>

            {/* Checkout Button - Solo mostrar si está logueado */}
            {!isEmpty && isLoggedIn && (
                <button
                    onClick={() => navigate('/checkout')}
                    className="w-full bg-black dark:bg-white text-white dark:text-black py-4 px-6 font-bold text-sm uppercase hover:bg-gray-900 dark:hover:bg-zinc-200 transition-colors mb-4"
                >
                    CONTINUAR CON LA COMPRA
                </button>
            )}

            {/* Login Button - Solo mostrar si NO está logueado */}
            {!isLoggedIn && (
                <button
                    onClick={() => navigate('/login')}
                    className="w-full border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-gray-900 dark:text-zinc-100 py-4 px-6 font-bold text-sm uppercase hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors mb-6"
                >
                    INICIAR SESIÓN
                </button>
            )}

            {/* Mensaje cuando hay productos pero no está logueado */}
            {!isEmpty && !isLoggedIn && (
                <div className="text-center text-sm text-gray-600 dark:text-zinc-400 mb-4">
                    Inicia sesión para continuar con tu compra
                </div>
            )}

            {/* Payment Methods - Removido por seguridad */}
        </div>
    )
}
