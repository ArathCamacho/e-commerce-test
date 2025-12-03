import { createContext, useContext, useState, useEffect } from 'react'
import { CarritoService, obtenerClienteLocal } from '../services/apiservice'

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
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                setCartItems([])
                return
            }
            
            const response = await CarritoService.obtener(cliente.id_cliente)
            setCartItems(response.items || response.productos || [])
        } catch (error) {
            console.error('Error loading cart:', error)
            setCartItems([])
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
                    item => item.id_producto === product.id &&
                        item.color === product.color &&
                        item.talla === product.size
                )
                if (existingItem) {
                    return prevItems.map(item =>
                        item.id_producto === product.id &&
                            item.color === product.color &&
                            item.talla === product.size
                            ? { ...item, cantidad: (item.cantidad || item.quantity || 0) + 1 }
                            : item
                    )
                }
                return [...prevItems, {
                    ...product,
                    id_producto: product.id,
                    cantidad: 1,
                    precio_unitario: product.price || product.precio_unitario
                }]
            })

            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                showNotificationMsg("Debes iniciar sesión para agregar productos al carrito", "error")
                return
            }

            // Llamada al backend
            await CarritoService.agregar(
                cliente.id_cliente, 
                product.id, 
                1, 
                product.color, 
                product.size
            )

            // Recargar carrito
            await loadCart()
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
                i => i.id_producto === productId && i.color === color && i.talla === size
            )

            if (!item) return

            // Actualización optimista
            setCartItems(prevItems =>
                prevItems.filter(
                    item => !(item.id_producto === productId && item.color === color && item.talla === size)
                )
            )

            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) return

            // Llamada al backend
            await CarritoService.eliminarItem(item.id_item, cliente.id_cliente)
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
                    item.id_producto === productId && item.color === color && item.talla === size
                        ? { ...item, cantidad: quantity }
                        : item
                )
            )

            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) return

            // Encontrar el item
            const item = cartItems.find(
                i => i.id_producto === productId && i.color === color && i.talla === size
            )

            if (!item) return

            // Eliminar y agregar con nueva cantidad (workaround)
            await CarritoService.eliminarItem(item.id_item, cliente.id_cliente)
            await CarritoService.agregar(
                cliente.id_cliente,
                productId,
                quantity,
                color,
                item.talla
            )
            await loadCart()
        } catch (error) {
            console.error('Error updating quantity:', error)
            showNotificationMsg("Error al actualizar cantidad", "error")
            await loadCart()
        }
    }

    const clearCart = async () => {
        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) return
            
            setCartItems([])
            await CarritoService.vaciar(cliente.id_cliente)
        } catch (error) {
            console.error('Error clearing cart:', error)
            await loadCart()
        }
    }

    const cartCount = cartItems.reduce((total, item) => total + (parseInt(item.cantidad) || parseInt(item.quantity) || 0), 0)

    const cartTotal = cartItems.reduce((total, item) => {
        // Usar precio_unitario del backend (siempre float) y cantidad
        const price = parseFloat(item.precio_unitario) || 0
        const quantity = parseInt(item.cantidad) || parseInt(item.quantity) || 0
        return total + (price * quantity)
    }, 0)

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
