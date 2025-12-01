import api from './api'

/**
 * Servicio de métodos de pago
 * Maneja tarjetas y otros métodos de pago del usuario
 */
const paymentService = {
    /**
     * Obtener todos los métodos de pago del usuario
     * @returns {Promise} Response con array de métodos de pago
     */
    getPaymentMethods: async () => {
        try {
            const response = await api.get('/payment-methods')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener un método de pago específico
     * @param {number|string} paymentMethodId - ID del método de pago
     * @returns {Promise} Response con datos del método de pago
     */
    getPaymentMethodById: async (paymentMethodId) => {
        try {
            const response = await api.get(`/payment-methods/${paymentMethodId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Agregar un nuevo método de pago
     * @param {Object} paymentData - Datos del método de pago
     * @param {string} paymentData.cardNumber - Número de tarjeta
     * @param {string} paymentData.cardholderName - Nombre en la tarjeta
     * @param {string} paymentData.expirationDate - Fecha de expiración (MM/YY)
     * @param {string} paymentData.cvv - CVV
     * @param {number} paymentData.billingAddressId - ID de dirección de facturación
     * @param {boolean} paymentData.isDefault - Si es método predeterminado
     * @returns {Promise} Response con el método de pago creado
     */
    addPaymentMethod: async (paymentData) => {
        try {
            const response = await api.post('/payment-methods', paymentData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar un método de pago existente
     * @param {number|string} paymentMethodId - ID del método de pago
     * @param {Object} paymentData - Datos a actualizar
     * @returns {Promise} Response con el método de pago actualizado
     */
    updatePaymentMethod: async (paymentMethodId, paymentData) => {
        try {
            const response = await api.put(`/payment-methods/${paymentMethodId}`, paymentData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Eliminar un método de pago
     * @param {number|string} paymentMethodId - ID del método de pago
     * @returns {Promise} Response de confirmación
     */
    deletePaymentMethod: async (paymentMethodId) => {
        try {
            const response = await api.delete(`/payment-methods/${paymentMethodId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Establecer un método de pago como predeterminado
     * @param {number|string} paymentMethodId - ID del método de pago
     * @returns {Promise} Response con el método de pago actualizado
     */
    setDefaultPaymentMethod: async (paymentMethodId) => {
        try {
            const response = await api.put(`/payment-methods/${paymentMethodId}/set-default`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener método de pago predeterminado
     * @returns {Promise} Response con el método de pago predeterminado
     */
    getDefaultPaymentMethod: async () => {
        try {
            const response = await api.get('/payment-methods/default')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Verificar un método de pago
     * @param {number|string} paymentMethodId - ID del método de pago
     * @returns {Promise} Response de confirmación de verificación
     */
    verifyPaymentMethod: async (paymentMethodId) => {
        try {
            const response = await api.post(`/payment-methods/${paymentMethodId}/verify`)
            return response
        } catch (error) {
            throw error
        }
    },
}

export default paymentService
