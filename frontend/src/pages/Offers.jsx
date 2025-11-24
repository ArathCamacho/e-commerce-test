import React from "react";
import { Link } from "react-router-dom";

export default function Ofertas() {

    const ofertas = [
        {
            name: "Hoodie Premium Gris",
            desc: "Sudadera de algodón suave",
            before: "$899",
            price: "$699",
            img: "/placeholder.jpg",
        },
        {
            name: "Pantalón Jogger Negro",
            desc: "Tela ligera y fresca",
            before: "$799",
            price: "$549",
            img: "/placeholder.jpg",
        },
        {
            name: "Tenis Urban Street",
            desc: "Comodidad para uso diario",
            before: "$1299",
            price: "$999",
            img: "/placeholder.jpg",
        },
        {
            name: "Playera Oversize Blanca",
            desc: "Diseño moderno, corte amplio",
            before: "$399",
            price: "$249",
            img: "/placeholder.jpg",
        },
        {
            name: "Chamarra Casual Café",
            desc: "Ideal para clima templado",
            before: "$1499",
            price: "$1099",
            img: "/placeholder.jpg",
        },
        {
            name: "Pantalón Cargo Beige",
            desc: "Material resistente",
            before: "$899",
            price: "$699",
            img: "/placeholder.jpg",
        },
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 py-10">

            {/* TÍTULO */}
            <h1 className="text-3xl font-semibold mb-8">Ofertas</h1>

            {/* GRID DE PRODUCTOS EN DESCUENTO */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-3 gap-8">

                {ofertas.map((p, i) => (
                    <Link 
                        to={`/producto/${i}`} 
                        key={i}
                        className="cursor-pointer group"
                    >
                        {/* Imagen */}
                        <div className="w-full h-[380px] rounded-lg overflow-hidden">
                            <img
                                src={p.img}
                                alt={p.name}
                                className="w-full h-full object-cover group-hover:scale-105 transition"
                            />
                        </div>

                        {/* Texto */}
                        <h3 className="mt-3 text-sm font-medium">{p.name}</h3>
                        <p className="text-xs text-gray-600">{p.desc}</p>

                        {/* Precios */}
                        <div className="mt-1 flex items-center gap-2">
                            <span className="font-semibold text-black">{p.price}</span>
                            <span className="text-gray-400 line-through text-sm">{p.before}</span>
                        </div>
                    </Link>
                ))}

            </div>

        </div>
    );
}
