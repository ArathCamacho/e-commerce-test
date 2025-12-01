import { createContext, useContext, useState, useEffect } from 'react'
import cartService from '../services/cartService'

const CartContext = createContext()

export function CartProvider({ children }) {
    const [cartItems, setCartItems] = useState([])
    const [notification, setNotification] = useState({ show: false, message: '', type: 'success' })
    const [loading, setLoading] = useState(false)

    // Cargar carrito al montar el componente
    useEffect(() => {
        loadCart()
    }, [])

    const loadCart = async () => {
        try {
            const response = await cartService.getCart()
            setCartItems(response.data.items || [])
        } catch (error) {
            console.error('Error loading cart:', error)
            // Si falla, continuar con carrito vacío (usuario no autenticado)
        }
    }

    const showNotificationMsg = (message, type = 'success') => {
        setNotification({ show: true, message, type })
        setTimeout(() => setNotification({ show: false, message: '', type: 'success' }), 3000)
    }

    const addToCart = async (product) => {
        try {
            setLoading(true)

            // Actualización optimista del UI
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

            // Llamada al backend
            const response = await cartService.addToCart({
                productId: product.id,
                quantity: 1,
                size: product.size,
                color: product.color
            })

            // Actualizar con datos del servidor
            setCartItems(response.data.items || cartItems)
            showNotificationMsg("Producto agregado al carrito exitosamente", "success")
        } catch (error) {
            console.error('Error adding to cart:', error)
            showNotificationMsg("Error al agregar producto al carrito", "error")
            // Revertir cambio optimista en caso de error
            await loadCart()
        } finally {
            setLoading(false)
        }
    }

    const removeFromCart = async (productId, color, size) => {
        try {
            // Encontrar el item para obtener su ID en el backend
            const item = cartItems.find(
                i => i.id === productId && i.color === color && i.size === size
            )

            if (!item) return

            // Actualización optimista
            setCartItems(prevItems =>
                prevItems.filter(
                    item => !(item.id === productId && item.color === color && item.size === size)
                )
            )

            // Llamada al backend
            await cartService.removeFromCart(item.cartItemId || item.id)
        } catch (error) {
            console.error('Error removing from cart:', error)
            showNotificationMsg("Error al eliminar producto", "error")
            await loadCart()
        }
    }

    const updateQuantity = async (productId, color, size, quantity) => {
        if (quantity <= 0) {
            removeFromCart(productId, color, size)
            return
        }

        try {
            // Actualización optimista
            setCartItems(prevItems =>
                prevItems.map(item =>
                    item.id === productId && item.color === color && item.size === size
                        ? { ...item, quantity }
                        : item
                )
            )

            // Encontrar el item
            const item = cartItems.find(
                i => i.id === productId && i.color === color && i.size === size
            )

            if (!item) return

            // Llamada al backend
            await cartService.updateCartItem(item.cartItemId || item.id, quantity)
        } catch (error) {
            console.error('Error updating quantity:', error)
            showNotificationMsg("Error al actualizar cantidad", "error")
            await loadCart()
        }
    }

    const clearCart = async () => {
        try {
            setCartItems([])
            await cartService.clearCart()
        } catch (error) {
            console.error('Error clearing cart:', error)
            await loadCart()
        }
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
                loading,
                showNotification: showNotificationMsg,
                addToCart,
                removeFromCart,
                updateQuantity,
                clearCart,
                loadCart,
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
