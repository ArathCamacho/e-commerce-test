import { useCart } from '../../context/CartContext'

export function ProductInfo({
    product,
    selectedColor,
    setSelectedColor,
    selectedSize,
    setSelectedSize,
    currentColorData
}) {
    const { addToCart, showNotification } = useCart()

    const handleAddToCart = () => {
        if (!selectedColor && !selectedSize) {
            showNotification("Por favor selecciona un color y una talla", "error")
            return
        }
        if (!selectedColor) {
            showNotification("Por favor selecciona un color", "error")
            return
        }
        if (!selectedSize) {
            showNotification("Por favor selecciona una talla", "error")
            return
        }

        addToCart({
            id: product.id,
            name: product.name,
            price: product.price,
            color: currentColorData?.name,
            size: selectedSize,
            image: currentColorData?.thumbnail
        })
    }

    return (
        <div className="w-full lg:w-[60%] h-full px-4 md:px-12 lg:px-20 flex flex-col justify-center">
            <div className="max-w-xl">
                {/* Product Title and Price */}
                <div className="mb-8">
                    <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-zinc-100 mb-2 uppercase tracking-wide">
                        {product.name}
                    </h1>
                    <p className="text-xl font-bold text-gray-900 dark:text-zinc-100">
                        {product.price}
                    </p>
                </div>

                {/* Color Selector */}
                <div className="mb-8">
                    <label className="block text-sm font-medium text-gray-700 dark:text-zinc-300 mb-3">
                        Color: {currentColorData ? currentColorData.name : 'Selecciona un color'}
                    </label>
                    <div className="flex flex-wrap">
                        {product.colors.map((color) => (
                            <button
                                key={color.id}
                                onClick={() => setSelectedColor(color.id)}
                                className={`relative w-24 h-32 border transition-all focus:outline-none ${selectedColor === color.id
                                        ? "border-black dark:border-white ring-1 ring-black dark:ring-white z-10"
                                        : "border-gray-200 dark:border-zinc-700 hover:border-gray-400 dark:hover:border-zinc-500"
                                    }`}
                            >
                                <img
                                    src={color.thumbnail}
                                    alt={color.name}
                                    className="w-full h-full object-cover"
                                />
                            </button>
                        ))}
                    </div>
                </div>

                {/* Size Selector */}
                <div className="mb-8">
                    <label className="block text-sm font-medium text-gray-700 dark:text-zinc-300 mb-3 uppercase">
                        SELECCIONE LA TALLA
                    </label>
                    <div className="flex flex-wrap">
                        {product.sizes.map((size) => {
                            const isSelected = selectedSize === size.name;
                            const isOutOfStock = !size.inStock;

                            return (
                                <button
                                    key={size.name}
                                    onClick={() => !isOutOfStock && setSelectedSize(size.name)}
                                    disabled={isOutOfStock}
                                    className={`w-24 py-4 text-sm font-medium border transition-all focus:outline-none relative ${isOutOfStock
                                            ? "border-gray-200 dark:border-zinc-700 text-gray-300 dark:text-zinc-600 cursor-not-allowed"
                                            : isSelected
                                                ? "border-black dark:border-white bg-black dark:bg-white text-white dark:text-black ring-1 ring-black dark:ring-white z-10"
                                                : "border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-gray-900 dark:text-zinc-100 hover:border-gray-400 dark:hover:border-zinc-500"
                                        }`}
                                >
                                    {size.name}
                                    {isOutOfStock && (
                                        <div className="absolute inset-0 pointer-events-none">
                                            <svg className="w-full h-full text-gray-300 dark:text-zinc-600" viewBox="0 0 100 100" preserveAspectRatio="none">
                                                <line x1="0" y1="0" x2="100" y2="100" stroke="currentColor" strokeWidth="1" />
                                                <line x1="100" y1="0" x2="0" y2="100" stroke="currentColor" strokeWidth="1" />
                                            </svg>
                                        </div>
                                    )}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Size Guide Link */}
                <div className="mb-8">
                    <a
                        href="#"
                        className="text-sm font-medium text-gray-900 dark:text-zinc-100 underline hover:text-gray-600 dark:hover:text-zinc-400 transition-colors uppercase"
                    >
                        GUÍA DE TALLAS
                    </a>
                </div>

                {/* Add to Cart Button */}
                <button
                    onClick={handleAddToCart}
                    className="w-full bg-black dark:bg-white text-white dark:text-black py-4 px-6 font-bold text-sm uppercase hover:bg-gray-900 dark:hover:bg-zinc-200 transition-colors focus:outline-none"
                >
                    AGREGAR
                </button>
            </div>
        </div>
    )
}
