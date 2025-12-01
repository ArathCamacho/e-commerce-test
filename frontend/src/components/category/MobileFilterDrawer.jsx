import React from 'react';

export function MobileFilterDrawer({ isOpen, onClose, children }) {
    if (!isOpen) return null;

    return (
        <>
            {/* Overlay */}
            <div
                className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                onClick={onClose}
            ></div>

            {/* Drawer */}
            <div className="fixed top-0 left-0 bottom-0 w-80 bg-white dark:bg-zinc-900 z-50 lg:hidden overflow-y-auto">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-100">Filtros</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-600 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-zinc-100 text-2xl"
                        >
                            ✕
                        </button>
                    </div>
                    {children}
                </div>
            </div>
        </>
    );
}
