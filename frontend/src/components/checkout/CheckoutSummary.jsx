import { useCart } from '../../context/CartContext'
import { useNavigate } from 'react-router-dom'

export function CheckoutSummary() {
    const { cartTotal } = useCart()
    const navigate = useNavigate()
    const shippingCost = 140.00
    const total = cartTotal + shippingCost

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
                <div className="flex justify-between text-gray-700 dark:text-zinc-300">
                    <span>Costo estimado de envío</span>
                    <span>${shippingCost.toFixed(2)}</span>
                </div>
            </div>

            {/* Total */}
            <div className="flex justify-between text-base font-bold text-gray-900 dark:text-zinc-100 mb-6 pb-6 border-b border-gray-200 dark:border-zinc-800">
                <span>TOTAL</span>
                <span>${total.toFixed(2)}</span>
            </div>

            {/* Checkout Button */}
            <button
                onClick={() => navigate('/checkout')}
                className="w-full bg-black dark:bg-white text-white dark:text-black py-4 px-6 font-bold text-sm uppercase hover:bg-gray-900 dark:hover:bg-zinc-200 transition-colors mb-6"
            >
                CONTINUAR CON LA COMPRA
            </button>

            {/* Payment Methods */}
            <div className="flex items-center justify-center">
                <img
                    src="https://via.placeholder.com/300x40/FFFFFF/666666?text=Payment+Methods"
                    alt="Métodos de pago"
                    className="w-full max-w-xs"
                />
            </div>
        </div>
    )
}
