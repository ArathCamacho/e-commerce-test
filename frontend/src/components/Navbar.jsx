import { useState, useEffect } from "react"
import { NavbarLogo } from "./navbar/NavbarLogo"
import { NavbarLinks } from "./navbar/NavbarLinks"
import { NavbarIcons } from "./navbar/NavbarIcons"
import { MobileMenu } from "./navbar/MobileMenu"
import { SearchOverlay } from "./navbar/SearchOverlay"

export function Header() {
    const [scrollOpacity, setScrollOpacity] = useState(1)
    const [isDarkMode, setIsDarkMode] = useState(false)
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
    const [isSearchOpen, setIsSearchOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState("")

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

    const toggleSearch = () => {
        setIsSearchOpen(!isSearchOpen)
    }

    return (
        <>
            <header
                className="bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800 sticky top-0 z-50 transition-all duration-300"
                style={{ opacity: scrollOpacity }}
            >
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <NavbarLogo />
                    <NavbarLinks />
                    <NavbarIcons
                        isMobileMenuOpen={isMobileMenuOpen}
                        setIsMobileMenuOpen={setIsMobileMenuOpen}
                        isDarkMode={isDarkMode}
                        setIsDarkMode={setIsDarkMode}
                        toggleSearch={toggleSearch}
                    />
                </div>

                <MobileMenu
                    isOpen={isMobileMenuOpen}
                    onClose={() => setIsMobileMenuOpen(false)}
                />
            </header>

            <SearchOverlay
                isOpen={isSearchOpen}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                scrollOpacity={scrollOpacity}
            />
        </>
    )
}
