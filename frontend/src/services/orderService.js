import api from './api'

/**
 * Servicio de órdenes
 * Maneja la creación, consulta y gestión de órdenes
 */
const orderService = {
    /**
     * Obtener todas las órdenes del usuario
     * @param {Object} filters - Filtros opcionales
     * @param {string} filters.status - Filtrar por estado (pending, paid, shipped, delivered, cancelled)
     * @param {number} filters.page - Página actual
     * @param {number} filters.limit - Órdenes por página
     * @returns {Promise} Response con array de órdenes
     */
    getOrders: async (filters = {}) => {
        try {
            const response = await api.get('/orders', { params: filters })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener detalle de una orden específica
     * @param {number|string} orderId - ID de la orden
     * @returns {Promise} Response con datos de la orden
     */
    getOrderById: async (orderId) => {
        try {
            const response = await api.get(`/orders/${orderId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Crear una nueva orden
     * @param {Object} orderData - Datos de la orden
     * @param {number} orderData.shippingAddressId - ID de dirección de envío
     * @param {number} orderData.billingAddressId - ID de dirección de facturación
     * @param {number} orderData.paymentMethodId - ID del método de pago
     * @param {string} orderData.shippingMethod - Método de envío
     * @returns {Promise} Response con la orden creada
     */
    createOrder: async (orderData) => {
        try {
            const response = await api.post('/orders', orderData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Cancelar una orden
     * @param {number|string} orderId - ID de la orden
     * @param {string} reason - Razón de cancelación (opcional)
     * @returns {Promise} Response de confirmación
     */
    cancelOrder: async (orderId, reason = '') => {
        try {
            const response = await api.post(`/orders/${orderId}/cancel`, { reason })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener el estado de rastreo de una orden
     * @param {number|string} orderId - ID de la orden
     * @returns {Promise} Response con información de rastreo
     */
    trackOrder: async (orderId) => {
        try {
            const response = await api.get(`/orders/${orderId}/tracking`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar la dirección de envío de una orden
     * @param {number|string} orderId - ID de la orden
     * @param {number} addressId - ID de la nueva dirección
     * @returns {Promise} Response con la orden actualizada
     */
    updateShippingAddress: async (orderId, addressId) => {
        try {
            const response = await api.put(`/orders/${orderId}/shipping-address`, { addressId })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Procesar el pago de una orden
     * @param {number|string} orderId - ID de la orden
     * @param {Object} paymentData - Datos del pago
     * @returns {Promise} Response con confirmación de pago
     */
    processPayment: async (orderId, paymentData) => {
        try {
            const response = await api.post(`/orders/${orderId}/payment`, paymentData)
            return response
        } catch (error) {
            throw error
        }
    },
}

export default orderService
