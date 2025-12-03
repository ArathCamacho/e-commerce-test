import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ClienteService, guardarClienteLocal } from '../services/apiservice'

export function Login() {
    const navigate = useNavigate()
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await ClienteService.login(email, password)

            // Guardar datos del cliente
            if (response.id_cliente) {
                guardarClienteLocal(response)
            }

            // Redirigir a la página de inicio (home)
            navigate('/')
        } catch (error) {
            const errorMessage = error.response?.data?.message || 'Error al iniciar sesión. Por favor verifica tus credenciales.'
            setError(errorMessage)
            console.error('Login error:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-zinc-900 px-4 relative">
            {/* Back Button */}
            <Link
                to="/"
                className="absolute top-8 left-8 flex items-center gap-2 text-[rgb(77,76,76)] dark:text-zinc-400 hover:text-[rgb(169,191,162)] transition-colors"
            >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                </svg>
                <span className="text-sm font-medium">Volver al inicio</span>
            </Link>

            {/* Logo */}
            <div className="flex items-center gap-2 mb-8">
                <div className="w-10 h-10 rounded-full bg-[rgb(169,191,162)] flex items-center justify-center text-white font-bold text-xl">
                    V
                </div>
                <span className="text-xl font-bold text-[rgb(77,76,76)] dark:text-zinc-100 tracking-wide">
                    VANDENTIALS
                </span>
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold text-[rgb(77,76,76)] dark:text-zinc-100 mb-4">
                Iniciar Sesión
            </h1>

            {/* Error Message */}
            {error && (
                <div className="w-full max-w-[400px] mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 text-sm rounded">
                    {error}
                </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="w-full max-w-[400px] space-y-4">
                <input
                    type="email"
                    placeholder="Correo electrónico"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <div className="flex justify-end">
                    <Link
                        to="/forgot-password"
                        className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                    >
                        ¿Olvidaste tu contraseña?
                    </Link>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full h-[45px] bg-[rgb(169,191,162)] text-white text-base font-bold hover:bg-[rgb(159,181,152)] transition-colors mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                </button>

                <div className="text-center mt-6">
                    <span className="text-sm font-light text-[rgb(77,76,76)] dark:text-zinc-400">
                        ¿No tienes cuenta?{' '}
                    </span>
                    <Link
                        to="/register"
                        className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                    >
                        Regístrate aquí
                    </Link>
                </div>
            </form>
        </div>
    )
}
