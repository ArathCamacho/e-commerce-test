import React, { useState } from "react";
import { Link } from "react-router-dom"; // 🔥 AGREGADO

export default function Hombre() {

    // 🔥 AGREGAMOS IDs SIN CAMBIAR TUS DATOS
    const products = Array.from({ length: 12 }).map((_, i) => ({
        id: i + 1,
        name: "Asset",
        price: "$00.00",
        description: "Descripción",
        img: "/placeholder.jpg",
        tag: "Nuevo"
    }));

    const [openSort, setOpenSort] = useState(false);

    return (
        <div className="max-w-7xl mx-auto px-4 py-6 flex gap-10">

            {/* SIDEBAR */}
            <aside className="w-56 hidden lg:block">
                <h2 className="font-semibold text-xl mb-4">Mujeres (1103)</h2>

                <div className="mb-6">
                    <h3 className="font-semibold mb-2">Categorías</h3>
                    <ul className="text-sm text-gray-700 space-y-1">
                        <li className="cursor-pointer hover:text-black">Calzado</li>
                        <li className="cursor-pointer hover:text-black">Playeras y tops</li>
                        <li className="cursor-pointer hover:text-black">Shorts</li>
                        <li className="cursor-pointer hover:text-black">Sudaderas con y sin gorro</li>
                        <li className="cursor-pointer hover:text-black">Pants y tights</li>
                        <li className="cursor-pointer hover:text-black">Chamarras y chalecos</li>
                        <li className="cursor-pointer hover:text-black">Ropa interior deportiva</li>
                        <li className="cursor-pointer hover:text-black">Conjuntos</li>
                        <li className="cursor-pointer hover:text-black">Surf y trajes de baño</li>
                        <li className="cursor-pointer hover:text-black">Calcetines</li>
                        <li className="cursor-pointer hover:text-black">Accesorios y equipo</li>
                    </ul>
                </div>

                <div>
                    <h3 className="font-semibold mb-2">Comprar por precio</h3>
                    <label className="flex items-center text-sm gap-2">
                        <input type="checkbox" /> Menos de $1000
                    </label>
                    <label className="flex items-center text-sm gap-2">
                        <input type="checkbox" /> $2000 - $3000
                    </label>
                    <label className="flex items-center text-sm gap-2">
                        <input type="checkbox" /> Más de $3000
                    </label>
                </div>
            </aside>

            {/* CONTENIDO PRINCIPAL */}
            <main className="flex-1">

                {/* Barra superior */}
                <div className="flex items-center justify-between mb-4 relative">
                    <h2 className="text-xl font-semibold">Mujer</h2>

                    <div className="flex items-center gap-8 text-sm text-gray-600">

                        {/* BOTÓN ORDENAR POR */}
                        <button
                            onClick={() => setOpenSort(!openSort)}
                            className="hover:text-black flex items-center gap-2"
                        >
                            ORDENAR POR
                            <span className="text-lg">☰</span>
                        </button>

                        {/* MENÚ DESPLEGABLE */}
                        {openSort && (
                            <div className="absolute right-0 top-10 w-48 bg-white shadow-lg border rounded-md z-20 text-sm">
                                <button className="block w-full text-left px-4 py-2 hover:bg-gray-100">
                                    Mayor a menor precio
                                </button>
                                <button className="block w-full text-left px-4 py-2 hover:bg-gray-100">
                                    Menor a mayor precio
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* GRID DE PRODUCTOS */}
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
                    
                    {products.map((p, i) => (

                        <Link 
                            to={`/producto/${p.id}`}  // 🔥 AGREGA NAVEGACIÓN
                            key={p.id}
                            className="group border rounded-lg overflow-hidden hover:shadow-md transition cursor-pointer block"
                        >
                            <div className="relative">
                                <img
                                    src={p.img}
                                    alt=""
                                    className="w-full h-60 object-cover"
                                />

                                <span className="absolute bottom-2 right-2 bg-green-100 text-green-700 text-xs px-2 py-1 rounded">
                                    {p.tag}
                                </span>
                            </div>

                            <div className="p-3">
                                <h3 className="text-sm text-gray-900 font-medium">{p.name}</h3>
                                <p className="text-xs text-gray-500">{p.description}</p>
                                <p className="mt-1 font-semibold">{p.price}</p>
                            </div>
                        </Link>

                    ))}

                </div>
            </main>
        </div>
    );
}
