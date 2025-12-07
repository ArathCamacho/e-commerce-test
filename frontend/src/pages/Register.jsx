import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ClienteService, guardarClienteLocal } from '../services/apiservice'

export function Register() {
    const navigate = useNavigate()
    const [nombre, setNombre] = useState('')
    const [apellido, setApellido] = useState('')
    const [email, setEmail] = useState('')
    const [telefono, setTelefono] = useState('')
    const [password, setPassword] = useState('')
    const [passwordStrength, setPasswordStrength] = useState(0)
    const [passwordFeedback, setPasswordFeedback] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const calculateStrength = (pass) => {
        let score = 0
        if (!pass) return 0

        if (pass.length >= 8) score += 1
        if (/[A-Z]/.test(pass)) score += 1
        if (/[0-9]/.test(pass)) score += 1
        if (/[^A-Za-z0-9]/.test(pass)) score += 1

        return score
    }

    const getStrengthColor = (score) => {
        if (score === 0) return 'bg-gray-200 dark:bg-zinc-700'
        if (score <= 2) return 'bg-red-500'
        if (score === 3) return 'bg-yellow-500'
        return 'bg-green-500'
    }

    const getStrengthLabel = (score) => {
        if (score === 0) return ''
        if (score <= 2) return 'Débil'
        if (score === 3) return 'Media'
        return 'Fuerte'
    }

    const handlePasswordChange = (e) => {
        const newPassword = e.target.value
        setPassword(newPassword)
        const score = calculateStrength(newPassword)
        setPasswordStrength(score)
        setPasswordFeedback(getStrengthLabel(score))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)
        
        try {
            // Registrar nuevo cliente con los campos correctos del backend
            const response = await ClienteService.registrar({
                nombre: nombre,
                apellido: apellido,
                correo: email,
                telefono: telefono,
                contrasena: password
            })

            // Guardar datos del cliente
            if (response.id_cliente) {
                guardarClienteLocal(response)
            }

            // Redirigir a la página de inicio (home)
            navigate('/')
        } catch (error) {
            console.error('Register error:', error)
            const errorMessage = error.response?.data?.detail?.[0]?.msg 
                || error.response?.data?.message 
                || 'Error al registrar usuario. Por favor intenta de nuevo.'
            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-zinc-900 px-4">
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
                Regístrate
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
                    type="text"
                    placeholder="Nombre"
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    required
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <input
                    type="text"
                    placeholder="Apellido"
                    value={apellido}
                    onChange={(e) => setApellido(e.target.value)}
                    required
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <input
                    type="email"
                    placeholder="Correo electrónico"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <input
                    type="tel"
                    placeholder="Teléfono"
                    value={telefono}
                    onChange={(e) => setTelefono(e.target.value)}
                    required
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <div className="space-y-2">
                    <input
                        type="password"
                        placeholder="Contraseña"
                        value={password}
                        onChange={handlePasswordChange}
                        className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                    />

                    {/* Password Strength Indicator */}
                    {password && (
                        <div className="space-y-1">
                            <div className="flex gap-1 h-1">
                                {[1, 2, 3, 4].map((level) => (
                                    <div
                                        key={level}
                                        className={`flex-1 rounded-full transition-colors duration-300 ${passwordStrength >= level
                                                ? getStrengthColor(passwordStrength)
                                                : 'bg-gray-200 dark:bg-zinc-700'
                                            }`}
                                    />
                                ))}
                            </div>
                            <p className={`text-xs text-right transition-colors duration-300 ${passwordStrength <= 2 ? 'text-red-500' :
                                    passwordStrength === 3 ? 'text-yellow-500' : 'text-green-500'
                                }`}>
                                {passwordFeedback}
                            </p>
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={passwordStrength < 3 || loading}
                    className={`w-full h-[45px] text-white text-base font-bold transition-colors mt-4 ${
                        passwordStrength < 3 || loading
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-[rgb(169,191,162)] hover:bg-[rgb(159,181,152)]'
                    }`}
                >
                    {loading ? 'Creando cuenta...' : 'Crear cuenta'}
                </button>

                <div className="text-center mt-6">
                    <span className="text-sm font-light text-[rgb(77,76,76)] dark:text-zinc-400">
                        ¿Ya tienes cuenta?{' '}
                    </span>
                    <Link
                        to="/login"
                        className="text-sm font-light text-[rgb(169,191,162)] hover:underline"
                    >
                        Inicia Sesión
                    </Link>
                </div>
            </form>
        </div>
    )
}
