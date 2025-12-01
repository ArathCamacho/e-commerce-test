import { createContext, useContext, useState } from 'react'

const CartContext = createContext()

export function CartProvider({ children }) {
    const [cartItems, setCartItems] = useState([])
    const [notification, setNotification] = useState({ show: false, message: '', type: 'success' })

    const showNotificationMsg = (message, type = 'success') => {
        setNotification({ show: true, message, type })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 3000)
    }

    const addToCart = (product) => {
        setCartItems(prevItems => {
            const existingItem = prevItems.find(
                item => item.id === product.id &&
                    item.color === product.color &&
                    item.size === product.size
            )
            if (existingItem) {
                return prevItems.map(item =>
                    item.id === product.id &&
                        item.color === product.color &&
                        item.size === product.size
                        ? { ...item, quantity: item.quantity + 1 }
                        : item
                )
            }
            return [...prevItems, { ...product, quantity: 1 }]
        })

        // Show success notification
        showNotificationMsg("Producto agregado al carrito exitosamente", "success")
    }

    const removeFromCart = (productId, color, size) => {
        setCartItems(prevItems =>
            prevItems.filter(
                item => !(item.id === productId && item.color === color && item.size === size)
            )
        )
    }

    const updateQuantity = (productId, color, size, quantity) => {
        if (quantity <= 0) {
            removeFromCart(productId, color, size)
            return
        }

        setCartItems(prevItems =>
            prevItems.map(item =>
                item.id === productId && item.color === color && item.size === size
                    ? { ...item, quantity }
                    : item
            )
        )
    }

    const clearCart = () => {
        setCartItems([])
    }

    const cartCount = cartItems.reduce((total, item) => total + item.quantity, 0)

    const cartTotal = cartItems.reduce(
        (total, item) => total + parseFloat(item.price.replace('$', '')) * item.quantity,
        0
    )

    return (
        <CartContext.Provider
            value={{
                cartItems,
                cartCount,
                cartTotal,
                notification,
                showNotification: showNotificationMsg,
                addToCart,
                removeFromCart,
                updateQuantity,
                clearCart,
            }}
        >
            {children}
        </CartContext.Provider>
    )
}

export function useCart() {
    const context = useContext(CartContext)
    if (!context) {
        throw new Error('useCart must be used within a CartProvider')
    }
    return context
}
