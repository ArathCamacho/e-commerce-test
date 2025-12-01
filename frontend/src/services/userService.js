import api from './api'

/**
 * Servicio de usuario
 * Maneja el perfil y datos personales del usuario
 */
const userService = {
    /**
     * Obtener perfil del usuario actual
     * @returns {Promise} Response con datos del perfil
     */
    getUserProfile: async () => {
        try {
            const response = await api.get('/user/profile')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar perfil del usuario
     * @param {Object} userData - Datos a actualizar
     * @param {string} userData.firstName - Nombre
     * @param {string} userData.lastName - Apellido
     * @param {string} userData.email - Email
     * @param {string} userData.phone - Teléfono
     * @returns {Promise} Response con perfil actualizado
     */
    updateUserProfile: async (userData) => {
        try {
            const response = await api.put('/user/profile', userData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Cambiar contraseña del usuario
     * @param {string} oldPassword - Contraseña actual
     * @param {string} newPassword - Nueva contraseña
     * @returns {Promise} Response de confirmación
     */
    changePassword: async (oldPassword, newPassword) => {
        try {
            const response = await api.put('/user/password', { oldPassword, newPassword })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar información personal
     * @param {Object} info - Información personal
     * @returns {Promise} Response con datos actualizados
     */
    updatePersonalInfo: async (info) => {
        try {
            const response = await api.put('/user/personal-info', info)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Eliminar cuenta de usuario
     * @param {string} password - Contraseña para confirmar
     * @returns {Promise} Response de confirmación
     */
    deleteAccount: async (password) => {
        try {
            const response = await api.delete('/user/account', { data: { password } })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener preferencias del usuario
     * @returns {Promise} Response con preferencias
     */
    getPreferences: async () => {
        try {
            const response = await api.get('/user/preferences')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Actualizar preferencias del usuario
     * @param {Object} preferences - Preferencias a actualizar
     * @returns {Promise} Response con preferencias actualizadas
     */
    updatePreferences: async (preferences) => {
        try {
            const response = await api.put('/user/preferences', preferences)
            return response
        } catch (error) {
            throw error
        }
    },
}

export default userService
