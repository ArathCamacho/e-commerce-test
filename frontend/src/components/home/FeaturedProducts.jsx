import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Heart } from 'lucide-react'
import { useLikes } from '../../context/LikesContext'
import { ProductoService } from '../../services/apiservice'

export function FeaturedProducts() {
    const { toggleLike, checkIsLiked } = useLikes()
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                setLoading(true)
                const response = await ProductoService.obtenerCatalogo()
                const productList = response.productos || response || []
                setProducts(productList.slice(0, 8))
            } catch (error) {
                console.error('Error loading featured products:', error)
                setError('No se pud ieron cargar los productos')
                // Fallback a productos de ejemplo si falla la petición
                setProducts([
                    {
                        id: 1,
                        image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
                    },
                    {
                        id: 2,
                        image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
                    },
                    {
                        id: 3,
                        image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
                    },
                    {
                        id: 4,
                        image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
                    },
                ])
            } finally {
                setLoading(false)
            }
        }

        fetchProducts()
    }, [])

    return (
        <section className="py-12 md:py-16 bg-gray-50 dark:bg-zinc-950 transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header con Título y Botón */}
                <div className="flex items-center justify-between mb-12">
                    <h2 className="text-2xl md:text-2xl font-bold text-gray-700 dark:text-zinc-200">PRODUCTOS DESTACADOS</h2>
                    <a href="#" className="text-gray-700 dark:text-zinc-400 text-base font-bold transition relative group hover:scale-105 transition-transform duration-300">
                        VER TODOS
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12">
                        <p className="text-gray-600 dark:text-zinc-400">Cargando productos...</p>
                    </div>
                )}

                {/* Error State */}
                {error && !loading && (
                    <div className="text-center py-12">
                        <p className="text-red-600 dark:text-red-400">{error}</p>
                    </div>
                )}

                {/* Grid de Productos */}
                {!loading && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {products.map((product) => (
                            <Link
                                key={product.id}
                                to={`/producto/${product.id}`}
                                className="bg-white dark:bg-zinc-900 rounded-lg overflow-hidden group cursor-pointer transition-colors duration-300 hover:shadow-lg hover:scale-105 transition-transform duration-700 ease-[cubic-bezier(.15,.83,.66,1)]"
                            >
                                <div className="relative h-64 md:h-72 overflow-hidden bg-gray-200 dark:bg-zinc-800">
                                    <img
                                        src={product.image || "/placeholder.svg"}
                                        alt={`Producto ${product.id}`}
                                        className="w-full h-full object-cover transition duration-300"
                                    />
                                    <button
                                        onClick={(e) => {
                                            e.preventDefault()
                                            const isLiked = checkIsLiked(product.id)
                                            toggleLike(product)
                                            window.dispatchEvent(new CustomEvent('product-like-changed', {
                                                detail: { type: isLiked ? 'remove' : 'add' }
                                            }))
                                        }}
                                        className="absolute top-4 right-4 p-2 rounded-full bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm shadow-sm hover:scale-110 transition-transform duration-200 z-10"
                                    >
                                        <Heart
                                            className={`w-5 h-5 ${checkIsLiked(product.id) ? 'fill-red-500 text-red-500' : 'text-gray-600 dark:text-zinc-300'}`}
                                        />
                                    </button>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </section >
    )
}
