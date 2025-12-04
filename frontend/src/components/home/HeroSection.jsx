export function HeroSection() {
    return (
        <section className="relative h-96 md:h-[500px] overflow-hidden">
            {/* Background Image */}
            <div
                className="absolute inset-0 bg-cover bg-center"
                style={{
                    backgroundImage: "url(https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=600&fit=crop)",
                }}
            >
                {/* Overlay */}
                <div className="absolute inset-0 bg-black/40"></div>
            </div>

            {/* Content */}
            <div className="relative h-full flex flex-col items-center justify-center text-center px-4">
                <h1 className="text-4xl md:text-5xl font-bold mb-4 text-balance text-white">VISTE COMO NOSOTROS</h1>
                <p className="text-base md:text-lg text-white/90 mb-8 max-w-md">
                    Te traemos lo más reciente de nuestro catálogo con precios ideales
                </p>

                {/* Botones */}
                <div className="flex gap-4 flex-wrap justify-center">
                    <button className="bg-transparent border border-white text-white hover:bg-white hover:text-black px-6 py-2 rounded font-medium transition-colors hover:scale-105 transition-transform duration-300">
                        Ver colección
                    </button>
                    <button className="bg-transparent border border-white text-white hover:bg-white hover:text-black px-6 py-2 rounded font-medium transition-colors hover:scale-105 transition-transform duration-300">
                        Ver novedades
                    </button>
                </div>
            </div>
        </section>
    )
}
