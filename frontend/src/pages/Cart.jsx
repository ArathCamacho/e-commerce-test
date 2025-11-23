import { CartItemList } from '../components/cart/CartItemList'
import { CartSummary } from '../components/cart/CartSummary'

export function Cart() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900 transition-colors duration-300 py-8">
            <div className="max-w-7xl mx-auto px-4">
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-8">

                    {/* Left Column - Cart Items */}
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-zinc-100 mb-8 uppercase">
                            BOLSA DE COMPRAS
                        </h1>
                        <CartItemList />
                    </div>

                    {/* Right Column - Summary */}
                    <CartSummary />
                </div>
            </div>
        </div>
    )
}
