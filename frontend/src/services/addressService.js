import api from './api'

/**
 * Servicio de direcciones
 * Maneja direcciones de envío y facturación del usuario
 */
const addressService = {
    /**
     * Obtener todas las direcciones del usuario
     * @returns {Promise} Response con array de direcciones
     */
    getAddresses: async () => {
        try {
            const response = await api.get('/addresses')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener una dirección específica
     * @param {number|string} addressId - ID de la dirección
     * @returns {Promise} Response con datos de la dirección
     */
    getAddressById: async (addressId) => {
        try {
            const response = await api.get(`/addresses/${addressId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Crear una nueva dirección
     * @param {Object} addressData - Datos de la dirección
     * @param {string} addressData.firstName - Nombre
     * @param {string} addressData.lastName - Apellido
     * @param {string} addressData.address1 - Dirección línea 1
     * @param {string} addressData.address2 - Dirección línea 2 (opcional)
     * @param {string} addressData.city - Ciudad
     * @param {string} addressData.state - Estado
     * @param {string} addressData.postalCode - Código postal
     * @param {string} addressData.country - País
     * @param {string} addressData.phone - Teléfono
     * @param {boolean} addressData.isDefault - Si es dirección predeterminada
     * @returns {Promise} Response con la dirección creada
     */
    createAddress: async (addressData) => {
        try {
            const response = await api.post('/addresses', addressData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar una dirección existente
     * @param {number|string} addressId - ID de la dirección
     * @param {Object} addressData - Datos de la dirección
     * @returns {Promise} Response con la dirección actualizada
     */
    updateAddress: async (addressId, addressData) => {
        try {
            const response = await api.put(`/addresses/${addressId}`, addressData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Eliminar una dirección
     * @param {number|string} addressId - ID de la dirección
     * @returns {Promise} Response de confirmación
     */
    deleteAddress: async (addressId) => {
        try {
            const response = await api.delete(`/addresses/${addressId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Establecer una dirección como predeterminada
     * @param {number|string} addressId - ID de la dirección
     * @returns {Promise} Response con la dirección actualizada
     */
    setDefaultAddress: async (addressId) => {
        try {
            const response = await api.put(`/addresses/${addressId}/set-default`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener dirección predeterminada
     * @returns {Promise} Response con la dirección predeterminada
     */
    getDefaultAddress: async () => {
        try {
            const response = await api.get('/addresses/default')
            return response
        } catch (error) {
            throw error
        }
    },
}

export default addressService
