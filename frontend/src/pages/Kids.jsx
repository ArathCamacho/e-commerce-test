import React, { useState } from "react";
import { Filter } from "lucide-react";
import { ProductCard } from "../components/category/ProductCard";
import { CategorySidebar } from "../components/category/CategorySidebar";

export default function Ninos() {
    const products = Array.from({ length: 12 }).map((_, i) => ({
        id: i + 1,
        name: "Asset",
        price: "$00.00",
        description: "Descripción",
        img: "/placeholder.jpg",
        tag: "Añadir"
    }));

    const [openSort, setOpenSort] = useState(false);
    const [openFilters, setOpenFilters] = useState(false);

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 transition-colors duration-300">
            <div className="max-w-screen-2xl mx-auto px-6 lg:px-8 py-8 flex gap-8">

                {/* SIDEBAR - Desktop */}
                <CategorySidebar
                    title="Niños"
                    count={69}
                    showGenderFilter={true}
                    categories={[
                        "Calzado",
                        "Playeras y tops",
                        "Shorts",
                        "Sudaderas con y sin gorro",
                        "Pants y tights",
                        "Chamarras y chalecos",
                        "Ropa interior deportiva",
                        "Conjuntos",
                        "Surf y trajes de baño",
                        "Calcetines",
                        "Accesorios y equipo"
                    ]}
                />

                {/* Mobile Filter Drawer */}
                {openFilters && (
                    <>
                        {/* Overlay */}
                        <div
                            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                            onClick={() => setOpenFilters(false)}
                        ></div>

                        {/* Drawer */}
                        <div className="fixed top-0 left-0 bottom-0 w-80 bg-white dark:bg-zinc-900 z-50 lg:hidden overflow-y-auto">
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-100">Filtros</h2>
                                    <button
                                        onClick={() => setOpenFilters(false)}
                                        className="text-gray-600 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-zinc-100 text-2xl"
                                    >
                                        ✕
                                    </button>
                                </div>
                                <CategorySidebar
                                    title="Niños"
                                    count={69}
                                    showGenderFilter={true}
                                    categories={[
                                        "Calzado",
                                        "Playeras y tops",
                                        "Shorts",
                                        "Sudaderas con y sin gorro",
                                        "Pants y tights",
                                        "Chamarras y chalecos",
                                        "Ropa interior deportiva",
                                        "Conjuntos",
                                        "Surf y trajes de baño",
                                        "Calcetines",
                                        "Accesorios y equipo"
                                    ]}
                                />
                            </div>
                        </div>
                    </>
                )}

                {/* CONTENIDO PRINCIPAL */}
                <main className="flex-1 min-w-0">
                    {/* HEADER */}
                    <div className="flex items-center justify-between mb-6">
                        {/* Mobile Filter Button */}
                        <button
                            onClick={() => setOpenFilters(true)}
                            className="lg:hidden flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-zinc-700 text-gray-700 dark:text-zinc-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
                        >
                            <Filter className="w-4 h-4" />
                            <span className="text-sm font-medium">Filtros</span>
                        </button>

                        {/* Title - Hidden on mobile when filter button shows */}
                        <h2 className="hidden lg:block text-2xl font-bold text-gray-900 dark:text-zinc-100">Niños</h2>

                        {/* BOTÓN ORDENAR POR */}
                        <div className="relative ml-auto">
                            <button
                                onClick={() => setOpenSort(!openSort)}
                                className="text-gray-700 dark:text-zinc-300 hover:text-gray-900 dark:hover:text-zinc-100 flex items-center gap-2 font-medium transition-colors text-sm"
                            >
                                ORDENAR POR
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>

                            {/* MENÚ DESPLEGABLE */}
                            {openSort && (
                                <div className="absolute right-0 top-12 w-56 bg-white dark:bg-zinc-900 shadow-lg border border-gray-200 dark:border-zinc-800 z-20 text-sm">
                                    <button className="block w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-zinc-800 text-gray-700 dark:text-zinc-300 transition-colors">
                                        Mayor a menor precio
                                    </button>
                                    <button className="block w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-zinc-800 text-gray-700 dark:text-zinc-300 transition-colors">
                                        Menor a mayor precio
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* GRID DE PRODUCTOS */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {products.map((p) => (
                            <ProductCard key={p.id} product={p} />
                        ))}
                    </div>
                </main>
            </div>
        </div>
    );
}
