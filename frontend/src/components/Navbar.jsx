import { Search, Heart, ShoppingCart, User, Moon, Sun } from "lucide-react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useCart } from "../context/CartContext"

export function Header() {
    const [scrollOpacity, setScrollOpacity] = useState(1)
    const [isDarkMode, setIsDarkMode] = useState(false)
    const navigate = useNavigate()
    const { cartCount } = useCart()
    const [isAnimatingCart, setIsAnimatingCart] = useState(false)
    const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false)

    useEffect(() => {
        if (cartCount > 0) {
            setIsAnimatingCart(true)
            const timer = setTimeout(() => setIsAnimatingCart(false), 300)
            return () => clearTimeout(timer)
        }
    }, [cartCount])

    useEffect(() => {
        const handleScroll = () => {
            const scrollPosition = window.scrollY
            const opacity = Math.max(0, 1 - scrollPosition / 300)
            setScrollOpacity(opacity)
        }

        window.addEventListener("scroll", handleScroll)
        return () => window.removeEventListener("scroll", handleScroll)
    }, [])

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add("dark")
        } else {
            document.documentElement.classList.remove("dark")
        }
    }, [isDarkMode])

    return (
        <header
            className="bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800 sticky top-0 z-50 transition-all duration-300"
            style={{ opacity: scrollOpacity }}
        >
            <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                {/* Logo */}
                <a href="/" className="flex items-center gap-2">
                    <div className="w-10 h-10 bg-[#A9BFA2] rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">V</span>
                    </div>
                    <span className="text-lg font-bold text-gray-600 dark:text-zinc-200 tracking-wide">
                        <span className="text-[#A9BFA2]">VAND</span>ENTIALS
                    </span>
                </a>

                {/* Navegación Central */}
                <nav className="hidden md:flex items-center gap-8">
                    <a
                        href="#"
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                    >
                        Mujer
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                    <a
                        href="#"
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                    >
                        Hombre
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                    <a
                        href="#"
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                    >
                        Niños
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                    <a
                        href="#"
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                    >
                        Novedades
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                    <a
                        href="#"
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                    >
                        Ofertas
                        <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                    </a>
                </nav>

                {/* Iconos Derecha */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsDarkMode(!isDarkMode)}
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-2 relative"
                        aria-label="Toggle dark mode"
                    >
                        <Moon
                            className={`w-5 h-5 absolute transition-all duration-500 ${isDarkMode ? "rotate-180 opacity-0" : "rotate-0 opacity-100"
                                }`}
                        />
                        <Sun
                            className={`w-5 h-5 transition-all duration-500 ${isDarkMode ? "rotate-0 opacity-100" : "-rotate-180 opacity-0"
                                }`}
                        />
                    </button>
                    <button
                        onClick={() => navigate('/favoritos')}
                        className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-2"
                    >
                        <Heart className="w-5 h-5" />
                    </button>
                    <button className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-2">
                        <Search className="w-5 h-5" />
                    </button>
                    <button
                        onClick={() => navigate('/cart')}
                        className={`text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-all duration-300 p-2 relative ${isAnimatingCart ? 'scale-125 text-black dark:text-white' : 'scale-100'
                            }`}
                    >
                        <ShoppingCart className="w-5 h-5" />
                        {cartCount > 0 && (
                            <span className={`absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center transition-transform duration-300 ${isAnimatingCart ? 'scale-125' : 'scale-100'
                                }`}>
                                {cartCount}
                            </span>
                        )}
                    </button>
                    <div className="relative">
                        <button
                            onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
                            className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-2"
                        >
                            <User className="w-5 h-5" />
                        </button>

                        {/* Dropdown Menu */}
                        {isUserDropdownOpen && (
                            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 shadow-lg z-50">
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
                                    onClick={() => {
                                        navigate('/login')
                                        setIsUserDropdownOpen(false)
                                    }}
                                    className="w-full text-left px-4 py-3 text-sm text-gray-900 dark:text-zinc-100 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors uppercase border-t border-gray-200 dark:border-zinc-800"
                                >
                                    Iniciar Sesión
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}
