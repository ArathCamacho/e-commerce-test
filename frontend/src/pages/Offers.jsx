import React from "react";
import { ProductCard } from "../components/category/ProductCard";

export default function Ofertas() {

    const ofertas = [
        {
            id: 1,
            name: "Hoodie Premium Gris",
            desc: "Sudadera de algodón suave",
            before: "$899",
            price: "$699",
            img: "/placeholder.jpg",
        },
        {
            id: 2,
            name: "Pantalón Jogger Negro",
            desc: "Tela ligera y fresca",
            before: "$799",
            price: "$549",
            img: "/placeholder.jpg",
        },
        {
            id: 3,
            name: "Tenis Urban Street",
            desc: "Comodidad para uso diario",
            before: "$1299",
            price: "$999",
            img: "/placeholder.jpg",
        },
        {
            id: 4,
            name: "Playera Oversize Blanca",
            desc: "Diseño moderno, corte amplio",
            before: "$399",
            price: "$249",
            img: "/placeholder.jpg",
        },
        {
            id: 5,
            name: "Chamarra Casual Café",
            desc: "Ideal para clima templado",
            before: "$1499",
            price: "$1099",
            img: "/placeholder.jpg",
        },
        {
            id: 6,
            name: "Pantalón Cargo Beige",
            desc: "Material resistente",
            before: "$899",
            price: "$699",
            img: "/placeholder.jpg",
        },
    ];

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 transition-colors duration-300">
            <div className="max-w-screen-2xl mx-auto px-6 lg:px-8 py-12">

                {/* TÍTULO */}
                <h1 className="text-4xl font-bold mb-12 text-gray-900 dark:text-zinc-100">Ofertas</h1>

                {/* GRID DE PRODUCTOS EN DESCUENTO */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {ofertas.map((p) => (
                        <ProductCard
                            key={p.id}
                            product={{ ...p, description: p.desc, badge: "OFERTA" }}
                            showAddButton={false}
                        />
                    ))}
                </div>

            </div>
        </div>
    );
}
