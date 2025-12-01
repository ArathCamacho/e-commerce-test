import { Heart, HeartOff } from 'lucide-react'
import { useEffect, useState } from 'react'

export function LikeNotification() {
    const [notifications, setNotifications] = useState([])
    const [navbarVisible, setNavbarVisible] = useState(true)

    useEffect(() => {
        const handleScroll = () => {
            // Simple check: if scrolled down more than 100px, assume navbar might be hidden or we want notification higher
            // But user said: "if navbar is not visible, move animation up"
            // Usually navbar is sticky, but let's assume standard behavior or check opacity
            // The user mentioned "if navbar is not visible", let's check scroll position
            // If scroll > 50, we can consider it "scrolled" and maybe adjust position
            // But let's look at the Header component logic. It has scrollOpacity.
            // If scroll > 300, opacity is 0.
            const scrollPosition = window.scrollY
            setNavbarVisible(scrollPosition < 300)
        }

        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        const handleLikeEvent = (event) => {
            const { type } = event.detail // 'add' or 'remove'
            const id = Date.now()
            setNotifications(prev => [...prev, { id, type }])

            setTimeout(() => {
                setNotifications(prev => prev.filter(n => n.id !== id))
            }, 1000)
        }

        window.addEventListener('product-like-changed', handleLikeEvent)
        return () => window.removeEventListener('product-like-changed', handleLikeEvent)
    }, [])

    return (
        <div
            className={`fixed right-4 z-50 pointer-events-none transition-all duration-300 ${navbarVisible ? 'top-20' : 'top-4'
                }`}
        >
            {notifications.map((notification) => (
                <div
                    key={notification.id}
                    className="mb-2 animate-like-notification"
                >
                    <div className="bg-white dark:bg-zinc-800 rounded-full p-3 shadow-lg flex items-center justify-center">
                        {notification.type === 'add' ? (
                            <Heart className="w-6 h-6 fill-red-500 text-red-500 animate-heart-beat" />
                        ) : (
                            <HeartOff className="w-6 h-6 text-gray-400 dark:text-zinc-500 animate-heart-shake" />
                        )}
                    </div>
                </div>
            ))}
        </div>
    )
}
