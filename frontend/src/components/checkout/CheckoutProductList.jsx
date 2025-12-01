import { useCart } from '../../context/CartContext'

export function CheckoutProductList() {
    const { cartItems } = useCart()

    // Agrupar productos por ID (mismo producto, diferentes variantes)
    const groupedProducts = cartItems.reduce((acc, item) => {
        const existingGroup = acc.find(group => group.id === item.id)

        if (existingGroup) {
            existingGroup.variants.push({
                color: item.color,
                size: item.size,
                quantity: item.quantity,
                image: item.image
            })
        } else {
            acc.push({
                id: item.id,
                name: item.name,
                price: item.price,
                variants: [{
                    color: item.color,
                    size: item.size,
                    quantity: item.quantity,
                    image: item.image
                }]
            })
        }

        return acc
    }, [])

    return (
        <div>
            <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 mb-4 uppercase">
                PAQUETE
            </h2>
            <p className="text-xs text-gray-600 dark:text-zinc-400 mb-4">
                Enviado por Vandentials
            </p>

            <div className="space-y-6">
                {groupedProducts.map((product) => (
                    <div key={product.id} className="border-b border-gray-200 dark:border-zinc-800 pb-6 last:border-b-0">
                        {/* Mostrar imagen del primer variant */}
                        <div className="w-20 h-24 bg-gray-100 dark:bg-zinc-800 mb-4">
                            <img
                                src={product.variants[0].image || "https://via.placeholder.com/80x96/E5E7EB/9CA3AF?text=Producto"}
                                alt={product.name}
                                className="w-full h-full object-cover"
                            />
                        </div>

                        {/* Información del producto */}
                        <div className="text-sm space-y-2">
                            <h3 className="font-bold text-gray-900 dark:text-zinc-100 uppercase">
                                {product.name}
                            </h3>
                            <p className="text-gray-700 dark:text-zinc-300 font-medium">
                                {product.price}
                            </p>

                            {/* Listar todas las variantes */}
                            <div className="space-y-1 text-xs text-gray-600 dark:text-zinc-400">
                                {product.variants.map((variant, idx) => (
                                    <div key={idx}>
                                        <p>Color: {variant.color}</p>
                                        <p>Talla: {variant.size}</p>
                                        <p>Cantidad: {variant.quantity}</p>
                                        {idx < product.variants.length - 1 && (
                                            <div className="h-px bg-gray-200 dark:bg-zinc-700 my-2" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
