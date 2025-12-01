import api from './api'

/**
 * Servicio de carrito de compras
 * Maneja todas las operaciones del carrito
 */
const cartService = {
    /**
     * Obtener el carrito actual del usuario
     * @returns {Promise} Response con el carrito y sus items
     */
    getCart: async () => {
        try {
            const response = await api.get('/cart')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Agregar un producto al carrito
     * @param {Object} item - Datos del item a agregar
     * @param {number} item.productId - ID del producto
     * @param {number} item.quantity - Cantidad
     * @param {string} item.size - Talla seleccionada
     * @param {string} item.color - Color seleccionado
     * @returns {Promise} Response con el carrito actualizado
     */
    addToCart: async (item) => {
        try {
            const response = await api.post('/cart/items', item)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar la cantidad de un item en el carrito
     * @param {number|string} itemId - ID del item en el carrito
     * @param {number} quantity - Nueva cantidad
     * @returns {Promise} Response con el carrito actualizado
     */
    updateCartItem: async (itemId, quantity) => {
        try {
            const response = await api.put(`/cart/items/${itemId}`, { quantity })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Eliminar un item del carrito
     * @param {number|string} itemId - ID del item en el carrito
     * @returns {Promise} Response con el carrito actualizado
     */
    removeFromCart: async (itemId) => {
        try {
            const response = await api.delete(`/cart/items/${itemId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Vaciar el carrito completamente
     * @returns {Promise} Response de confirmación
     */
    clearCart: async () => {
        try {
            const response = await api.delete('/cart')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Aplicar un cupón de descuento al carrito
     * @param {string} couponCode - Código del cupón
     * @returns {Promise} Response con el carrito actualizado
     */
    applyCoupon: async (couponCode) => {
        try {
            const response = await api.post('/cart/coupon', { code: couponCode })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Remover cupón de descuento del carrito
     * @returns {Promise} Response con el carrito actualizado
     */
    removeCoupon: async () => {
        try {
            const response = await api.delete('/cart/coupon')
            return response
        } catch (error) {
            throw error
        }
    },
}

export default cartService
