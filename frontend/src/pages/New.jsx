import React from "react";
import { HeroCarousel } from "../components/category/HeroCarousel";

export default function Novedades() {

    const destacados = [
        {
            id: 1,
            name: "Hoodie Oversize Beige",
            desc: "Sudadera cómoda para uso diario con un estilo moderno y relajado.",
            price: "$899",
            img: "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?q=80&w=2070&auto=format&fit=crop",
        },
        {
            id: 2,
            name: "Pantalón Cargo Negro",
            desc: "Diseño utilitario con múltiples bolsillos y corte ergonómico.",
            price: "$749",
            img: "https://images.unsplash.com/photo-1517445312882-5627b9311357?q=80&w=2069&auto=format&fit=crop",
        },
        {
            id: 3,
            name: "Playera Básica Blanca",
            desc: "Esencial de guardarropa, corte regular 100% algodón premium.",
            price: "$299",
            img: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=1780&auto=format&fit=crop",
        },
        {
            id: 4,
            name: "Chamarra Denim",
            desc: "Estilo clásico reinventado con detalles modernos y durabilidad.",
            price: "$1,299",
            img: "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?q=80&w=1887&auto=format&fit=crop",
        }
    ];

    return (
        <div className="h-[calc(100vh-73px)] bg-gray-50 dark:bg-zinc-950 overflow-hidden">
            <HeroCarousel products={destacados} />

            {/* Optional: Additional grid below if needed, but user asked to focus on carousel */}
            {/* We can add a small "Ver todo" section or just leave it as a showcase */}
        </div>
    );
}
