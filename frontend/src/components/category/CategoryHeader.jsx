import React from 'react';
import { Filter } from "lucide-react";

export function CategoryHeader({ title, onOpenFilters, openSort, setOpenSort }) {
    return (
        <div className="flex items-center justify-between mb-6">
            {/* Mobile Filter Button */}
            <button
                onClick={onOpenFilters}
                className="lg:hidden flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-zinc-700 text-gray-700 dark:text-zinc-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
            >
                <Filter className="w-4 h-4" />
                <span className="text-sm font-medium">Filtros</span>
            </button>

            {/* Title - Hidden on mobile when filter button shows */}
            <h2 className="hidden lg:block text-2xl font-bold text-gray-900 dark:text-zinc-100">{title}</h2>

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
    );
}
