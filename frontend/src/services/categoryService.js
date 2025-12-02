import api from './api'

/**
 * Servicio de categorías
 * Maneja la obtención de categorías y productos por categoría
 */
const categoryService = {
    /**
     * Obtener todas las categorías
     * @returns {Promise} Response con array de categorías
     */
    getCategories: async () => {
        try {
            const response = await api.get('/categories')
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener una categoría específica
     * @param {string} categorySlug - Slug de la categoría
     * @returns {Promise} Response con datos de la categoría
     */
    getCategoryBySlug: async (categorySlug) => {
        try {
            const response = await api.get(`/categories/${categorySlug}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener categorías recomendadas
     * @param {number} limit - Número de categorías
     * @returns {Promise} Response con array de categorías recomendadas
     */
    getRecommendedCategories: async (limit = 6) => {
        try {
            const response = await api.get('/categories/recommended', { params: { limit } })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos de una categoría
     * @param {string} categorySlug - Slug de la categoría
     * @param {Object} filters - Filtros opcionales (precio, talla, color, etc.)
     * @returns {Promise} Response con array de productos
     */
    getCategoryProducts: async (categorySlug, filters = {}) => {
        try {
            const response = await api.get(`/categories/${categorySlug}/products`, {
                params: filters
            })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener subcategorías de una categoría
     * @param {string} categorySlug - Slug de la categoría padre
     * @returns {Promise} Response con array de subcategorías
     */
    getSubcategories: async (categorySlug) => {
        try {
            const response = await api.get(`/categories/${categorySlug}/subcategories`)
            return response
        } catch (error) {
            throw error
        }
    },
}

export default categoryService
