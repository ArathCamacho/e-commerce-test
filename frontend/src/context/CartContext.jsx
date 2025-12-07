import { createContext, useContext, useState, useEffect } from 'react'
import { CarritoService, obtenerClienteLocal } from '../services/apiservice'

const CartContext = createContext()

export function CartProvider({ children }) {
    const [cartItems, setCartItems] = useState([])
    const [notification, setNotification] = useState({ show: false, message: '', type: 'success' })
    const [loading, setLoading] = useState(false)
    const [operationInProgress, setOperationInProgress] = useState(false)

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
        // Prevenir operaciones concurrentes
        if (operationInProgress) {
            console.log('Operación en progreso, ignorando...')
            return
        }

        setOperationInProgress(true)

        // Guardar estado anterior para posible reversión
        const previousItems = [...cartItems]

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
                setCartItems(previousItems) // Revertir
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
            setCartItems(previousItems)
        } finally {
            setLoading(false)
            setOperationInProgress(false)
        }
    }

    const removeFromCart = async (productId, color, size) => {
        // Prevenir operaciones concurrentes
        if (operationInProgress) {
            console.log('Operación en progreso, ignorando eliminación...')
            return
        }

        setOperationInProgress(true)

        // Guardar estado anterior para posible reversión
        const previousItems = [...cartItems]

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
            if (!cliente?.id_cliente) {
                setCartItems(previousItems) // Revertir
                return
            }

            // Llamada al backend
            await CarritoService.eliminarItem(item.id_item, cliente.id_cliente)

            // Sincronizar con backend
            await loadCart()
        } catch (error) {
            console.error('Error removing from cart:', error)
            showNotificationMsg("Error al eliminar producto", "error")
            // Revertir cambio optimista en caso de error
            setCartItems(previousItems)
        } finally {
            setOperationInProgress(false)
        }
    }

    const updateQuantity = async (productId, color, size, quantity) => {
        if (quantity <= 0) {
            removeFromCart(productId, color, size)
            return
        }

        // Prevenir operaciones concurrentes
        if (operationInProgress) {
            console.log('Operación en progreso, esperando...')
            return
        }

        setOperationInProgress(true)

        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                return
            }

            // Encontrar el item actual para calcular la diferencia
            const currentItem = cartItems.find(
                i => i.id_producto === productId && i.color === color && i.talla === size
            )

            const currentQuantity = currentItem ? (currentItem.cantidad || 0) : 0
            const difference = quantity - currentQuantity

            if (difference === 0) {
                // No hay cambio
                setOperationInProgress(false)
                return
            }

            if (difference > 0) {
                // Agregar la diferencia
                await CarritoService.agregar(
                    cliente.id_cliente,
                    productId,
                    difference,
                    color,
                    size
                )
            } else {
                // Para reducir, necesitamos eliminar y agregar
                if (currentItem && currentItem.id_item) {
                    try {
                        await CarritoService.eliminarItem(currentItem.id_item, cliente.id_cliente)
                        if (quantity > 0) {
                            await CarritoService.agregar(
                                cliente.id_cliente,
                                productId,
                                quantity,
                                color,
                                currentItem.talla
                            )
                        }
                    } catch (deleteError) {
                        console.log('Error al eliminar, recargando carrito')
                        await loadCart()
                        return
                    }
                }
            }

            // Recargar carrito del backend
            await loadCart()
        } catch (error) {
            console.error('Error updating quantity:', error)
            showNotificationMsg("Error al actualizar cantidad", "error")
            // Recargar para sincronizar
            await loadCart()
        } finally {
            setOperationInProgress(false)
        }
    }

    const clearCart = async () => {
        // Prevenir operaciones concurrentes
        if (operationInProgress) {
            console.log('Operación en progreso, ignorando vaciado...')
            return
        }

        setOperationInProgress(true)

        // Guardar estado anterior para posible reversión
        const previousItems = [...cartItems]

        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                setOperationInProgress(false)
                return
            }

            setCartItems([])
            await CarritoService.vaciar(cliente.id_cliente)

            // Sincronizar con backend
            await loadCart()
        } catch (error) {
            console.error('Error clearing cart:', error)
            // Revertir cambio optimista en caso de error
            setCartItems(previousItems)
        } finally {
            setOperationInProgress(false)
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
