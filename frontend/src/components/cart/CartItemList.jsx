import { Heart, Minus, Plus } from 'lucide-react'
import { useCart } from '../../context/CartContext'

export function CartItemList() {
    const { cartItems, updateQuantity } = useCart()

    if (cartItems.length === 0) {
        return <p className="text-gray-600 dark:text-zinc-400">Tu carrito está vacío</p>
    }

    return (
        <div className="space-y-6">
            {cartItems.map((item, index) => (
                <div
                    key={`${item.id}-${item.color}-${item.size}-${index}`}
                    className="flex gap-4 pb-6 border-b border-gray-200 dark:border-zinc-800"
                >
                    {/* Product Image */}
                    <div className="w-32 h-40 bg-gray-100 dark:bg-zinc-800 flex-shrink-0">
                        <img
                            src={item.image || "https://via.placeholder.com/128x160/E5E7EB/9CA3AF?text=Producto"}
                            alt={item.name}
                            className="w-full h-full object-cover"
                        />
                    </div>

                    {/* Product Details */}
                    <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                            <div>
                                <button className="mb-2">
                                    <Heart className="w-5 h-5 text-gray-700 dark:text-zinc-400" />
                                </button>
                                <h3 className="font-bold text-gray-900 dark:text-zinc-100 uppercase text-sm mb-1">
                                    {item.name}
                                </h3>
                                <p className="text-sm font-bold text-gray-900 dark:text-zinc-100">
                                    {item.price}
                                </p>
                            </div>
                        </div>

                        <div className="text-xs text-gray-600 dark:text-zinc-400 space-y-1 mb-4">
                            <p>Id de art. 008</p>
                            <p>Color: {item.color}</p>
                            <p>Talla: {item.size}</p>
                            <p>Cantidad: {item.quantity}</p>
                        </div>

                        {/* Quantity Controls */}
                        <div className="flex items-center gap-4">
                            <div className="flex items-center border border-gray-300 dark:border-zinc-700">
                                <button
                                    onClick={() => updateQuantity(item.id, item.color, item.size, item.quantity - 1)}
                                    className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
                                >
                                    <Minus className="w-4 h-4 text-gray-700 dark:text-zinc-400" />
                                </button>
                                <span className="px-4 text-sm font-medium text-gray-900 dark:text-zinc-100">
                                    {item.quantity}
                                </span>
                                <button
                                    onClick={() => updateQuantity(item.id, item.color, item.size, item.quantity + 1)}
                                    className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
                                >
                                    <Plus className="w-4 h-4 text-gray-700 dark:text-zinc-400" />
                                </button>
                            </div>

                            <p className="text-sm font-bold text-gray-900 dark:text-zinc-100">
                                Total: ${(parseFloat(item.price.replace('$', '')) * item.quantity).toFixed(2)}
                            </p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
