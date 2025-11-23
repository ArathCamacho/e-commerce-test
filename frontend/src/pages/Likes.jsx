import { Link } from 'react-router-dom'
import { Heart } from 'lucide-react'
import { useLikes } from '../context/LikesContext'

export function Likes() {
    const { likedProducts, toggleLike, checkIsLiked } = useLikes()

    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900 pt-24 pb-12 transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Mis Favoritos</h1>

                {likedProducts.length === 0 ? (
                    <div className="text-center py-12">
                        <Heart className="w-16 h-16 mx-auto text-gray-300 dark:text-zinc-700 mb-4" />
                        <p className="text-xl text-gray-500 dark:text-zinc-400">No tienes productos favoritos aún.</p>
                        <Link
                            to="/"
                            className="inline-block mt-6 px-6 py-2 bg-[rgb(169,191,162)] text-white rounded-md hover:bg-[rgb(159,181,152)] transition-colors"
                        >
                            Explorar productos
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {likedProducts.map((product) => (
                            <div
                                key={product.id}
                                className="bg-white dark:bg-zinc-900 rounded-lg overflow-hidden group relative hover:shadow-lg transition-all duration-300 border border-gray-100 dark:border-zinc-800"
                            >
                                <Link to={`/producto/${product.id}`}>
                                    <div className="relative h-64 md:h-72 overflow-hidden bg-gray-200 dark:bg-zinc-800">
                                        <img
                                            src={product.image || "/placeholder.svg"}
                                            alt={`Producto ${product.id}`}
                                            className="w-full h-full object-cover transition duration-300"
                                        />
                                    </div>
                                </Link>

                                <button
                                    onClick={(e) => {
                                        e.preventDefault()
                                        toggleLike(product)
                                    }}
                                    className="absolute top-4 right-4 p-2 rounded-full bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm shadow-sm hover:scale-110 transition-transform duration-200"
                                >
                                    <Heart
                                        className={`w-5 h-5 ${checkIsLiked(product.id) ? 'fill-red-500 text-red-500' : 'text-gray-600 dark:text-zinc-300'}`}
                                    />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
