import api from './api'

/**
 * Servicio de checkout
 * Maneja el proceso completo de checkout y pago
 */
const checkoutService = {
    /**
     * Obtener datos completos de checkout (carrito, direcciones, métodos de pago)
     * @returns {Promise} Response con todos los datos necesarios para checkout
     */
    getCheckoutData: async () => {
        try {
            const response = await api.get('/checkout')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar información de envío en el proceso de checkout
     * @param {Object} shippingData - Datos de envío
     * @param {number} shippingData.addressId - ID de dirección de envío
     * @param {string} shippingData.shippingMethod - Método de envío (standard, express, overnight)
     * @returns {Promise} Response con datos actualizados
     */
    updateShippingInfo: async (shippingData) => {
        try {
            const response = await api.put('/checkout/shipping', shippingData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar información de facturación
     * @param {Object} billingData - Datos de facturación
     * @param {number} billingData.addressId - ID de dirección de facturación
     * @returns {Promise} Response con datos actualizados
     */
    updateBillingInfo: async (billingData) => {
        try {
            const response = await api.put('/checkout/billing', billingData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar método de pago para el checkout
     * @param {Object} paymentData - Datos de pago
     * @param {number} paymentData.paymentMethodId - ID del método de pago
     * @returns {Promise} Response con datos actualizados
     */
    updatePaymentInfo: async (paymentData) => {
        try {
            const response = await api.put('/checkout/payment', paymentData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Procesar el pago y completar la orden
     * @param {Object} paymentData - Datos completos del pago
     * @param {number} paymentData.paymentMethodId - ID del método de pago
     * @param {number} paymentData.shippingAddressId - ID de dirección de envío
     * @param {number} paymentData.billingAddressId - ID de dirección de facturación
     * @param {string} paymentData.shippingMethod - Método de envío
     * @returns {Promise} Response con la orden creada y confirmación de pago
     */
    processPayment: async (paymentData) => {
        try {
            const response = await api.post('/checkout/process', paymentData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Confirmar y finalizar la orden
     * @param {Object} orderData - Datos finales de la orden
     * @returns {Promise} Response con la orden confirmada
     */
    confirmOrder: async (orderData) => {
        try {
            const response = await api.post('/checkout/confirm', orderData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Calcular el total del checkout incluyendo envío e impuestos
     * @param {Object} data - Datos para calcular
     * @param {string} data.shippingMethod - Método de envío
     * @param {string} data.couponCode - Código de cupón (opcional)
     * @returns {Promise} Response con desglose de costos
     */
    calculateTotal: async (data) => {
        try {
            const response = await api.post('/checkout/calculate', data)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener métodos de envío disponibles
     * @param {number} addressId - ID de dirección de envío
     * @returns {Promise} Response con métodos de envío y costos
     */
    getShippingMethods: async (addressId) => {
        try {
            const response = await api.get('/checkout/shipping-methods', { params: { addressId } })
            return response
        } catch (error) {
            throw error
        }
    },
}

export default checkoutService
