import api from './api'

/**
 * Servicio de autenticación
 * Maneja login, registro, logout y recuperación de contraseña
 */
const authService = {
    /**
     * Iniciar sesión
     * @param {string} email - Email del usuario
     * @param {string} password - Contraseña
     * @returns {Promise} Response con token y datos del usuario
     */
    login: async (email, password) => {
        try {
            const response = await api.post('/auth/login', { email, password })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Registrar nuevo usuario
     * @param {Object} userData - Datos del usuario
     * @param {string} userData.email - Email
     * @param {string} userData.password - Contraseña
     * @param {string} userData.firstName - Nombre
     * @param {string} userData.lastName - Apellido
     * @returns {Promise} Response con token y datos del usuario
     */
    register: async (userData) => {
        try {
            const response = await api.post('/auth/register', userData)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Cerrar sesión
     * @returns {Promise} Response de confirmación
     */
    logout: async () => {
        try {
            const response = await api.post('/auth/logout')
            // Limpiar localStorage
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            return response
        } catch (error) {
            // Limpiar localStorage incluso si falla la petición
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            throw error
        }
    },

    /**
     * Solicitar recuperación de contraseña
     * @param {string} email - Email del usuario
     * @returns {Promise} Response de confirmación
     */
    forgotPassword: async (email) => {
        try {
            const response = await api.post('/auth/forgot-password', { email })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Restablecer contraseña con token
     * @param {string} token - Token de recuperación
     * @param {string} newPassword - Nueva contraseña
     * @returns {Promise} Response de confirmación
     */
    resetPassword: async (token, newPassword) => {
        try {
            const response = await api.post('/auth/reset-password', { token, newPassword })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener usuario actual autenticado
     * @returns {Promise} Response con datos del usuario
     */
    getCurrentUser: async () => {
        try {
            const response = await api.get('/auth/me')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Verificar si hay una sesión activa
     * @returns {boolean} True si hay un token válido
     */
    isAuthenticated: () => {
        return !!localStorage.getItem('token')
    },

    /**
     * Obtener token actual
     * @returns {string|null} Token o null
     */
    getToken: () => {
        return localStorage.getItem('token')
    },
}

export default authService
