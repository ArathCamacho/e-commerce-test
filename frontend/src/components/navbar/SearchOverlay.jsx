import { Search } from "lucide-react"
import { useEffect } from "react"

export function SearchOverlay({ isOpen, searchQuery, setSearchQuery, scrollOpacity }) {

    // Auto-focus when opened
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => {
                document.getElementById('search-input')?.focus()
            }, 100)
        }
    }, [isOpen])

    return (
        <div
            className={`fixed top-[73px] left-0 right-0 z-40 overflow-hidden transition-all duration-500 ease-out ${isOpen ? 'max-h-24' : 'max-h-0'
                }`}
            style={{ opacity: isOpen ? scrollOpacity : 0 }}
        >
            <div className="max-w-7xl mx-auto px-4 py-4">
                <div className="relative">
                    <input
                        id="search-input"
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Buscar productos..."
                        className="w-full px-6 py-4 bg-white dark:bg-zinc-800 text-gray-900 dark:text-zinc-100 placeholder-gray-500 dark:placeholder-zinc-400 focus:outline-none transition-all duration-300 border-b-[6px] border-transparent focus:border-[#A9BFA2] caret-green"
                        style={{
                            caretColor: '#A9BFA2'
                        }}
                    />
                    <Search className="absolute right-6 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-zinc-500 pointer-events-none" />
                </div>
            </div>

            <style jsx>{`
                .caret-green {
                    caret-color: #A9BFA2;
                }
            `}</style>
        </div>
    )
}
