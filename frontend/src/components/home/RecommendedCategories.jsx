export function RecommendedCategories() {
    const categories = [
        {
            id: 1,
            name: "HOMBRES",
            image: "https://cdn0.uncomo.com/es/posts/3/0/4/estilos_de_moda_actuales_para_hombre_encuentra_el_tuyo_47403_600.webp",
        },
        {
            id: 2,
            name: "MUJERES",
            image: "https://mialuxury.me/wp-content/uploads/2021/10/Estilo-Clasico.jpg",
        },
        {
            id: 3,
            name: "NIÑOS",
            image: "https://sumaqmercados.pe/wp-content/uploads/2023/06/sumaq-mercados-blog-tipos-de-ropas-para-ninos.jpg.webp",
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
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {categories.map((category) => (
                        <div key={category.id} className="relative h-56 md:h-64 rounded-lg overflow-hidden group cursor-pointer">
                            {/* Imagen */}
                            <img
                                src={category.image}
                                alt={category.name}
                                className="w-full h-full object-cover transition duration-300"
                            />

                            {/* Overlay permanente oscuro */}
                            <div className="absolute inset-0 bg-black/40 group-hover:bg-black/60 transition duration-300"></div>

                            {/* Texto siempre visible */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <h3 className="text-white font-bold text-2xl md:text-3xl text-center drop-shadow-lg group-hover:scale-110 transition-transform duration-300">
                                    {category.name}
                                </h3>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
