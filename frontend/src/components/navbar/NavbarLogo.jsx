import { useNavigate } from "react-router-dom"

export function NavbarLogo() {
    const navigate = useNavigate()

    return (
        <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
        >
            <div className="w-10 h-10 bg-[#A9BFA2] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold text-lg">V</span>
            </div>
            <span className="hidden sm:inline text-lg font-bold text-gray-600 dark:text-zinc-200 tracking-wide">
                <span className="text-[#A9BFA2]">VAND</span>ENTIALS
            </span>
        </button>
    )
}
