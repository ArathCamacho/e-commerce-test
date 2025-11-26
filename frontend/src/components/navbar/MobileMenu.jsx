import { useNavigate } from "react-router-dom"

export function MobileMenu({ isOpen, onClose }) {
    const navigate = useNavigate()

    const handleNavigation = (path) => {
        navigate(path)
        onClose()
    }

    if (!isOpen) return null

    return (
        <>
            {/* Overlay */}
            <div
                className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                onClick={onClose}
            ></div>

            {/* Drawer */}
            <div className="fixed top-[73px] left-0 right-0 bottom-0 bg-white dark:bg-zinc-900 z-40 lg:hidden overflow-y-auto">
                <nav className="flex flex-col p-6 space-y-4">
                    <button
                        onClick={() => handleNavigation('/woman')}
                        className="text-left text-lg font-medium text-gray-900 dark:text-zinc-100 py-3 border-b border-gray-200 dark:border-zinc-800 hover:text-[#A9BFA2] transition-colors"
                    >
                        Mujer
                    </button>
                    <button
                        onClick={() => handleNavigation('/men')}
                        className="text-left text-lg font-medium text-gray-900 dark:text-zinc-100 py-3 border-b border-gray-200 dark:border-zinc-800 hover:text-[#A9BFA2] transition-colors"
                    >
                        Hombre
                    </button>
                    <button
                        onClick={() => handleNavigation('/kids')}
                        className="text-left text-lg font-medium text-gray-900 dark:text-zinc-100 py-3 border-b border-gray-200 dark:border-zinc-800 hover:text-[#A9BFA2] transition-colors"
                    >
                        Niños
                    </button>
                    <button
                        onClick={() => handleNavigation('/new')}
                        className="text-left text-lg font-medium text-gray-900 dark:text-zinc-100 py-3 border-b border-gray-200 dark:border-zinc-800 hover:text-[#A9BFA2] transition-colors"
                    >
                        Novedades
                    </button>
                    <button
                        onClick={() => handleNavigation('/offers')}
                        className="text-left text-lg font-medium text-gray-900 dark:text-zinc-100 py-3 border-b border-gray-200 dark:border-zinc-800 hover:text-[#A9BFA2] transition-colors"
                    >
                        Ofertas
                    </button>
                </nav>
            </div>
        </>
    )
}
