import api from './api'

/**
 * Servicio de productos
 * Maneja la obtención de productos, búsqueda, filtros y detalles
 */
const productService = {
    /**
     * Obtener lista de productos con filtros
     * @param {Object} params - Parámetros de filtrado
     * @param {string} params.category - Categoría
     * @param {number} params.page - Página actual
     * @param {number} params.limit - Productos por página
     * @param {string} params.sort - Orden (price_asc, price_desc, newest, popular)
     * @param {number} params.minPrice - Precio mínimo
     * @param {number} params.maxPrice - Precio máximo
     * @param {string} params.size - Talla
     * @param {string} params.color - Color
     * @returns {Promise} Response con array de productos
     */
    getProducts: async (params = {}) => {
        try {
            const response = await api.get('/products', { params })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener detalle de un producto específico
     * @param {number|string} productId - ID del producto
     * @returns {Promise} Response con datos del producto
     */
    getProductById: async (productId) => {
        try {
            const response = await api.get(`/products/${productId}`)
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos destacados
     * @param {number} limit - Número de productos a obtener
     * @returns {Promise} Response con array de productos destacados
     */
    getFeaturedProducts: async (limit = 8) => {
        try {
            const response = await api.get('/products/featured', { params: { limit } })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos de temporada/holiday
     * @param {number} limit - Número de productos a obtener
     * @returns {Promise} Response con array de productos de temporada
     */
    getHolidayProducts: async (limit = 8) => {
        try {
            const response = await api.get('/products/holiday', { params: { limit } })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Buscar productos por término de búsqueda
     * @param {string} query - Término de búsqueda
     * @param {Object} filters - Filtros adicionales
     * @returns {Promise} Response con array de productos
     */
    searchProducts: async (query, filters = {}) => {
        try {
            const response = await api.get('/products/search', {
                params: { q: query, ...filters }
            })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos por categoría
     * @param {string} categorySlug - Slug de la categoría (women, men, kids, etc.)
     * @param {Object} filters - Filtros opcionales
     * @returns {Promise} Response con array de productos
     */
    getProductsByCategory: async (categorySlug, filters = {}) => {
        try {
            const response = await api.get(`/products/category/${categorySlug}`, {
                params: filters
            })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos en oferta
     * @param {number} limit - Número de productos
     * @returns {Promise} Response con array de productos en oferta
     */
    getOfferProducts: async (limit = 12) => {
        try {
            const response = await api.get('/products/offers', { params: { limit } })
            return response
        } catch (error) {
            throw error
        }
    },

    /**
     * Obtener productos nuevos
     * @param {number} limit - Número de productos
     * @returns {Promise} Response con array de productos nuevos
     */
    getNewProducts: async (limit = 12) => {
        try {
            const response = await api.get('/products/new', { params: { limit } })
            return response
        } catch (error) {
            throw error
        }
    },
}

export default productService
