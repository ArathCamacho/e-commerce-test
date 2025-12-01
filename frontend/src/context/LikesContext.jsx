import { createContext, useContext, useState, useEffect } from 'react'

const LikesContext = createContext()

export function useLikes() {
    return useContext(LikesContext)
}

export function LikesProvider({ children }) {
    const [likedProducts, setLikedProducts] = useState(() => {
        const saved = localStorage.getItem('likedProducts')
        return saved ? JSON.parse(saved) : []
    })

    useEffect(() => {
        localStorage.setItem('likedProducts', JSON.stringify(likedProducts))
    }, [likedProducts])

    const toggleLike = (product) => {
        setLikedProducts(prev => {
            const isLiked = prev.some(p => p.id === product.id)
            if (isLiked) {
                return prev.filter(p => p.id !== product.id)
            } else {
                return [...prev, product]
            }
        })
    }

    const checkIsLiked = (productId) => {
        return likedProducts.some(p => p.id === productId)
    }

    const value = {
        likedProducts,
        toggleLike,
        checkIsLiked
    }

    return (
        <LikesContext.Provider value={value}>
            {children}
        </LikesContext.Provider>
    )
}
