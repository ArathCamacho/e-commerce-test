import api from './api'

/**
 * Servicio de likes/favoritos
 * Maneja los productos que le gustan al usuario
 */
const likeService = {
    /**
     * Obtener todos los productos que le gustan al usuario
     * @returns {Promise} Response con array de productos favoritos
     */
    getLikedProducts: async () => {
        try {
            const response = await api.get('/likes')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Dar like a un producto
     * @param {number|string} productId - ID del producto
     * @returns {Promise} Response de confirmación
     */
    likeProduct: async (productId) => {
        try {
            const response = await api.post('/likes', { productId })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Quitar like de un producto
     * @param {number|string} productId - ID del producto
     * @returns {Promise} Response de confirmación
     */
    unlikeProduct: async (productId) => {
        try {
            const response = await api.delete(`/likes/${productId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Verificar si un producto está marcado como favorito
     * @param {number|string} productId - ID del producto
     * @returns {Promise} Response con estado de like (true/false)
     */
    isProductLiked: async (productId) => {
        try {
            const response = await api.get(`/likes/${productId}/status`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Toggle like de un producto (dar like si no tiene, quitar si ya tiene)
     * @param {number|string} productId - ID del producto
     * @returns {Promise} Response con nuevo estado
     */
    toggleLike: async (productId) => {
        try {
            const response = await api.post(`/likes/${productId}/toggle`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener cantidad total de likes del usuario
     * @returns {Promise} Response con el número total de likes
     */
    getLikesCount: async () => {
        try {
            const response = await api.get('/likes/count')
            return response
        } catch (error) {
            throw error
        }
    },
}

export default likeService
