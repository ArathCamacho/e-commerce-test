import { Link } from 'react-router-dom'
import { CheckoutInfo } from '../components/checkout/CheckoutInfo'
import { CheckoutProductList } from '../components/checkout/CheckoutProductList'
import { CheckoutSummary } from '../components/checkout/CheckoutSummary'

export function Checkout() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900 transition-colors duration-300 py-8 relative">
            <div className="max-w-7xl mx-auto px-4">
                {/* Back Button */}
                <div className="mb-6">
                    <Link
                        to="/cart"
                        className="inline-flex items-center gap-2 text-[rgb(77,76,76)] dark:text-zinc-400 hover:text-[rgb(169,191,162)] transition-colors"
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M19 12H5M12 19l-7-7 7-7" />
                        </svg>
                        <span className="text-sm font-medium">Volver a la bolsa</span>
                    </Link>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 dark:text-zinc-100 mb-8 uppercase">
                    PROCESO DE COMPRA
                </h1>

                <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-8">

                    {/* Left Column - Checkout Info & Products */}
                    <div className="space-y-8">
                        <CheckoutInfo />

                        <div className="border-t border-gray-200 dark:border-zinc-800 pt-8">
                            <CheckoutProductList />
                        </div>
                    </div>

                    {/* Right Column - Summary */}
                    <CheckoutSummary />
                </div>
            </div>
        </div>
    )
}
