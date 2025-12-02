import axios from 'axios'

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'

// Crear instancia de axios
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Interceptor para agregar el token de autenticación a todas las peticiones
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Interceptor para manejar respuestas y errores globalmente
api.interceptors.response.use(
    (response) => {
        return response
    },
    (error) => {
        // Manejar errores de autenticación
        if (error.response?.status === 401) {
            // Token expirado o inválido
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/login'
        }

        // Manejar otros errores
        const errorMessage = error.response?.data?.message || error.message || 'Error en la petición'
        console.error('API Error:', errorMessage)

        return Promise.reject(error)
    }
)

export default api
