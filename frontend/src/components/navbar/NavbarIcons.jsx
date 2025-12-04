import { Search, Heart, ShoppingCart, User, Moon, Sun, Menu, X } from "lucide-react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useCart } from "../../context/CartContext"
import { obtenerClienteLocal, limpiarClienteLocal } from "../../services/apiservice"

export function NavbarIcons({
    isMobileMenuOpen,
    setIsMobileMenuOpen,
    isDarkMode,
    setIsDarkMode,
    toggleSearch
}) {
    const navigate = useNavigate()
    const { cartCount } = useCart()
    const [isAnimatingCart, setIsAnimatingCart] = useState(false)
    const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false)
    const [isLoggedIn, setIsLoggedIn] = useState(false)

    // Verificar si hay sesión activa
    useEffect(() => {
        const cliente = obtenerClienteLocal()
        setIsLoggedIn(!!cliente?.id_cliente)
    }, [])

    useEffect(() => {
        if (cartCount > 0) {
            setIsAnimatingCart(true)
            const timer = setTimeout(() => setIsAnimatingCart(false), 300)
            return () => clearTimeout(timer)
        }
    }, [cartCount])

    const handleLogout = () => {
        limpiarClienteLocal()
        setIsLoggedIn(false)
        setIsUserDropdownOpen(false)
        navigate('/')
    }

    return (
        <div className="flex items-center gap-1 sm:gap-2 md:gap-4">

            {/* Hamburger Menu - Tablet/Mobile */}
            <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 sm:p-2"
            >
                {isMobileMenuOpen ? <X className="w-5 h-5 sm:w-6 sm:h-6" /> : <Menu className="w-5 h-5 sm:w-6 sm:h-6" />}
            </button>

            <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 sm:p-2 relative"
            >
                <Moon className={`w-4 h-4 sm:w-5 sm:h-5 absolute transition-all duration-500 ${isDarkMode ? "rotate-180 opacity-0" : "rotate-0 opacity-100"}`} />
                <Sun className={`w-4 h-4 sm:w-5 sm:h-5 transition-all duration-500 ${isDarkMode ? "rotate-0 opacity-100" : "-rotate-180 opacity-0"}`} />
            </button>

            <button
                onClick={() => navigate('/favoritos')}
                className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 sm:p-2 hover:scale-110 transition-transform duration-300"
            >
                <Heart className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>

            <button
                onClick={toggleSearch}
                className="hidden xs:block text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 sm:p-2 hover:scale-110 transition-transform duration-300"
            >
                <Search className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>

            <button
                onClick={() => navigate('/cart')}
                className={`text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-all duration-300 p-1 sm:p-2 relative ${isAnimatingCart ? 'scale-125 text-black dark:text-white' : 'scale-100'}`}
            >
                <ShoppingCart className="w-4 h-4 sm:w-5 sm:h-5" />
                {cartCount > 0 && (
                    <span className={`absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-4 h-4 sm:w-5 sm:h-5 flex items-center justify-center transition-transform duration-300 ${isAnimatingCart ? 'scale-125' : 'scale-100'}`}>
                        {cartCount}
                    </span>
                )}
            </button>

            <div className="relative">
                <button
                    onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
                    className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 sm:p-2 hover:scale-110 transition-transform duration-300"
                >
                    <User className="w-4 h-4 sm:w-5 sm:h-5" />
                </button>

                {isUserDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 shadow-lg z-50">
                        {isLoggedIn ? (
                            <>
                                <button
                                    onClick={() => {
                                        navigate('/cuenta')
                                        setIsUserDropdownOpen(false)
                                    }}
                                    className="w-full text-left px-4 py-3 text-sm text-gray-900 dark:text-zinc-100 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors uppercase"
                                >
                                    Cuenta
                                </button>
                                <button
                                    onClick={handleLogout}
                                    className="w-full text-left px-4 py-3 text-sm text-gray-900 dark:text-zinc-100 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors uppercase border-t border-gray-200 dark:border-zinc-800"
                                >
                                    Cerrar Sesión
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => {
                                    navigate('/login')
                                    setIsUserDropdownOpen(false)
                                }}
                                className="w-full text-left px-4 py-3 text-sm text-gray-900 dark:text-zinc-100 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors uppercase"
                            >
                                Iniciar Sesión
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
