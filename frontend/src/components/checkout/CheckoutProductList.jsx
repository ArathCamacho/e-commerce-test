import { useCart } from '../../context/CartContext'

export function CheckoutProductList() {
    const { cartItems } = useCart()

    // Helper para obtener el precio como número
    const getPrice = (item) => {
        if (item.precio_unitario) {
            return parseFloat(item.precio_unitario)
        } else if (item.price) {
            return typeof item.price === 'string' 
                ? parseFloat(item.price.replace('$', '')) 
                : parseFloat(item.price)
        }
        return 0
    }

    // Helper para formatear el precio
    const formatPrice = (price) => {
        if (typeof price === 'number') {
            return `$${price.toFixed(2)}`
        } else if (typeof price === 'string') {
            return price.startsWith('$') ? price : `$${price}`
        }
        return '$0.00'
    }

    // Agrupar productos por ID (mismo producto, diferentes variantes)
    const groupedProducts = cartItems.reduce((acc, item) => {
        const existingGroup = acc.find(group => group.id === item.id)
        const itemPrice = getPrice(item)

        if (existingGroup) {
            existingGroup.variants.push({
                color: item.color,
                size: item.size,
                quantity: item.quantity,
                image: item.image || item.imagen
            })
        } else {
            acc.push({
                id: item.id,
                name: item.name || item.nombre_producto || 'Producto',
                price: itemPrice,
                variants: [{
                    color: item.color,
                    size: item.size,
                    quantity: item.quantity,
                    image: item.image || item.imagen
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
                                src={product.variants[0].image || "https://placehold.co/80x96/E5E7EB/9CA3AF?text=Producto"}
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
                                {formatPrice(product.price)}
                            </p>

                            {/* Listar todas las variantes */}
                            <div className="space-y-1 text-xs text-gray-600 dark:text-zinc-400">
                                {product.variants.map((variant, idx) => (
                                    <div key={idx}>
                                        <p>Color: {variant.color || 'N/A'}</p>
                                        <p>Talla: {variant.size || 'N/A'}</p>
                                        <p>Cantidad: {variant.quantity || 0}</p>
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
