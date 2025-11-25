import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";

export function HeroCarousel({ products }) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isAutoPlaying, setIsAutoPlaying] = useState(true);

    useEffect(() => {
        if (!isAutoPlaying) return;

        const interval = setInterval(() => {
            setCurrentIndex((prev) => (prev + 1) % products.length);
        }, 5000);

        return () => clearInterval(interval);
    }, [isAutoPlaying, products.length]);

    const nextSlide = () => {
        setCurrentIndex((prev) => (prev + 1) % products.length);
        setIsAutoPlaying(false);
    };

    const prevSlide = () => {
        setCurrentIndex((prev) => (prev - 1 + products.length) % products.length);
        setIsAutoPlaying(false);
    };

    return (
        <div className="relative w-full h-[calc(100vh-73px)] overflow-hidden bg-gray-900 group">
            {/* Slides */}
            {products.map((product, index) => (
                <div
                    key={product.id}
                    className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${index === currentIndex ? "opacity-100 z-10" : "opacity-0 z-0"
                        }`}
                >
                    {/* Background Image with Overlay */}
                    <div className="absolute inset-0">
                        <img
                            src={product.img}
                            alt={product.name}
                            className="w-full h-full object-cover opacity-60"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                    </div>

                    {/* Content */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-4 z-20">
                        <span className="text-[#A9BFA2] font-bold tracking-widest uppercase mb-4 animate-fade-in-up">
                            Nueva Colección
                        </span>
                        <h2 className="text-5xl md:text-7xl font-bold text-white mb-6 animate-fade-in-up delay-100">
                            {product.name}
                        </h2>
                        <p className="text-xl text-gray-200 mb-8 max-w-2xl animate-fade-in-up delay-200">
                            {product.desc}
                        </p>
                        <div className="flex gap-4 animate-fade-in-up delay-300">
                            <Link
                                to={`/producto/${product.id}`}
                                className="px-8 py-4 bg-white text-black font-bold text-lg hover:bg-[#A9BFA2] hover:text-white transition-colors duration-300"
                            >
                                Ver Producto
                            </Link>
                            <span className="px-8 py-4 border-2 border-white text-white font-bold text-lg">
                                {product.price}
                            </span>
                        </div>
                    </div>
                </div>
            ))}

            {/* Navigation Buttons */}
            <button
                onClick={prevSlide}
                className="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 transition-all z-30 opacity-0 group-hover:opacity-100"
            >
                <ChevronLeft className="w-8 h-8" />
            </button>
            <button
                onClick={nextSlide}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 transition-all z-30 opacity-0 group-hover:opacity-100"
            >
                <ChevronRight className="w-8 h-8" />
            </button>

            {/* Indicators */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3 z-30">
                {products.map((_, index) => (
                    <button
                        key={index}
                        onClick={() => {
                            setCurrentIndex(index);
                            setIsAutoPlaying(false);
                        }}
                        className={`w-3 h-3 rounded-full transition-all duration-300 ${index === currentIndex
                            ? "bg-[#A9BFA2] w-8"
                            : "bg-white/50 hover:bg-white"
                            }`}
                    />
                ))}
            </div>
        </div>
    );
}
