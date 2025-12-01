import { Link } from "react-router-dom";
import { Heart } from "lucide-react";
import { useLikes } from "../../context/LikesContext";

export function ProductCard({ product, showAddButton = true }) {
    const { toggleLike, checkIsLiked } = useLikes();
    const isLiked = checkIsLiked(product.id);

    const handleLikeClick = (e) => {
        e.preventDefault();
        toggleLike(product);
        window.dispatchEvent(new CustomEvent('product-like-changed', {
            detail: { type: isLiked ? 'remove' : 'add' }
        }));
    };

    return (
        <Link
            to={`/producto/${product.id}`}
            className="group bg-white dark:bg-zinc-900 overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer"
        >
            <div className="relative h-72 overflow-hidden bg-gray-100 dark:bg-zinc-800">
                <img
                    src={product.img || product.image}
                    alt={product.name}
                    className="w-full h-full object-cover transition duration-300"
                />

                {/* Añadir button - only show if enabled */}
                {showAddButton && product.tag && (
                    <button className="absolute bottom-4 right-4 bg-white/90 dark:bg-zinc-800/90 backdrop-blur-sm text-gray-900 dark:text-zinc-100 text-xs px-4 py-2 font-medium hover:bg-white dark:hover:bg-zinc-800 transition-all opacity-0 group-hover:opacity-100">
                        {product.tag}
                    </button>
                )}

                {/* Discount badge for offers */}
                {product.badge && (
                    <div className="absolute top-4 left-4 bg-red-500 text-white text-xs px-3 py-1 font-semibold">
                        {product.badge}
                    </div>
                )}

                {/* Heart button */}
                <button
                    onClick={handleLikeClick}
                    className="absolute top-4 right-4 p-2 bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm shadow-sm hover:scale-110 transition-transform duration-200 z-10"
                >
                    <Heart
                        className={`w-5 h-5 ${isLiked ? 'fill-red-500 text-red-500' : 'text-gray-600 dark:text-zinc-300'}`}
                    />
                </button>
            </div>

            <div className="p-4">
                <h3 className="text-sm text-gray-900 dark:text-zinc-100 font-medium mb-1">
                    {product.name}
                </h3>
                <p className="text-xs text-gray-500 dark:text-zinc-400 mb-2">
                    {product.description || product.desc}
                </p>

                {/* Price display - with or without discount */}
                {product.before ? (
                    <div className="flex items-center gap-2">
                        <span className="font-bold text-base text-gray-900 dark:text-zinc-100">
                            {product.price}
                        </span>
                        <span className="text-gray-400 dark:text-zinc-500 line-through text-sm">
                            {product.before}
                        </span>
                    </div>
                ) : (
                    <p className="font-semibold text-gray-900 dark:text-zinc-100">
                        {product.price}
                    </p>
                )}
            </div>
        </Link>
    );
}
