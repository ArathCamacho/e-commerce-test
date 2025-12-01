export function RecommendedCategories() {
    const categories = [
        {
            id: 1,
            name: "BUZOS",
            image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
        },
        {
            id: 2,
            name: "BERMUDAS",
            image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
        },
        {
            id: 3,
            name: "JEANS",
            image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
        },
        {
            id: 4,
            name: "SWEATERS",
            image: "https://www.hydroscand.dk/media/catalog/category//media/catalog/category/OG-Produkter-logo.png",
        },
    ]

    return (
        <section className="py-12 md:py-16 bg-white dark:bg-zinc-900 transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4">
                {/* Título */}
                <div className="mb-12 text-center">
                    <h2 className="text-2xl md:text-2xl font-bold text-gray-700 dark:text-zinc-200 mb-2">CATEGORÍAS RECOMENDADAS</h2>
                    <p className="text-gray-600 dark:text-zinc-400 text-sm md:text-base">Encuentra lo que necesites en nuestras secciones</p>
                </div>

                {/* Grid de Categorías */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {categories.map((category) => (
                        <div key={category.id} className="relative h-56 md:h-64 rounded-lg overflow-hidden group cursor-pointer">
                            {/* Imagen */}
                            <img
                                src={category.image}
                                alt={category.name}
                                className="w-full h-full object-cover transition duration-300"
                            />

                            {/* Overlay */}
                            <div className="absolute inset-0 bg-transparent group-hover:bg-white/20 transition duration-300"></div>

                            {/* Texto */}
                            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                <h3 className="text-white font-extralight text-2xl md:text-3xl text-center">{category.name}</h3>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
