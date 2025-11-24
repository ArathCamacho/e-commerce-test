import React from "react";
import { Link } from "react-router-dom";

export default function Novedades() {

    const destacados = [
        {
            name: "Hoodie Oversize Beige",
            desc: "Sudadera cómoda para uso diario",
            price: "$899",
            img: "/placeholder.jpg",
        },
        {
            name: "Pantalón Cargo Negro",
            desc: "Diseño moderno con múltiples bolsillos",
            price: "$749",
            img: "/placeholder.jpg",
        },
        {
            name: "Playera Básica Blanca",
            desc: "Corte regular 100% algodón",
            price: "$299",
            img: "/placeholder.jpg",
        },
    ];

    const iconos = [
        { name: "Hoodies", img: "/placeholder.jpg" },
        { name: "Pants", img: "/placeholder.jpg" },
        { name: "Pantalones", img: "/placeholder.jpg" },
        { name: "Playeras", img: "/placeholder.jpg" },
        { name: "Chamarras", img: "/placeholder.jpg" },
        { name: "Tenis", img: "/placeholder.jpg" },
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 py-10">

            {/* TÍTULO */}
            <h1 className="text-3xl font-semibold mb-8">Novedades</h1>

            {/* PRODUCTOS DESTACADOS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">

                {destacados.map((p, i) => (
                    <Link 
                        to={`/producto/${i}`} 
                        key={i} 
                        className="cursor-pointer"
                    >
                        <img
                            src={p.img}
                            alt={p.name}
                            className="w-full h-[450px] object-cover rounded-lg"
                        />

                        <h3 className="mt-3 text-sm font-medium">{p.name}</h3>
                        <p className="text-xs text-gray-600">{p.desc}</p>
                        <p className="font-semibold mt-1">{p.price}</p>
                    </Link>
                ))}

            </div>

            {/* SUBTÍTULO */}
            <h2 className="text-2xl font-semibold mb-4">Comprar por categoría</h2>

            {/* CARRUSEL DE ICONOS */}
            <div className="flex gap-6 overflow-x-auto pb-4">

                {iconos.map((i, idx) => (
                    <Link
                        to={`/producto/${idx}`}
                        key={idx}
                        className="min-w-[220px] cursor-pointer"
                    >
                        <div className="bg-gray-800 rounded-xl overflow-hidden h-40 flex items-center justify-center">
                            <img
                                src={i.img}
                                alt={i.name}
                                className="w-full h-full object-cover"
                            />
                        </div>

                        <p className="mt-2 text-center text-sm font-medium">
                            {i.name}
                        </p>
                    </Link>
                ))}

            </div>

        </div>
    );
}
