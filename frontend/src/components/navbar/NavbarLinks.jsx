import { useNavigate } from "react-router-dom"

export function NavbarLinks() {
    const navigate = useNavigate()

    const links = [
        { name: "Mujer", path: "/woman" },
        { name: "Hombre", path: "/men" },
        { name: "Niños", path: "/kids" },
        { name: "Novedades", path: "/new" },
        { name: "Ofertas", path: "/offers" },
    ]

    return (
        <nav className="hidden md:flex items-center gap-8">
            {links.map((link) => (
                <button
                    key={link.path}
                    onClick={() => navigate(link.path)}
                    className="text-gray-700 dark:text-zinc-400 hover:text-black dark:hover:text-white text-sm font-medium transition relative group"
                >
                    {link.name}
                    <span className="absolute top-full left-0 w-0 h-px bg-[#A9BFA2] transition-all group-hover:w-full mt-1"></span>
                </button>
            ))}
        </nav>
    )
}
