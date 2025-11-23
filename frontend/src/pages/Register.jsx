import { useState } from 'react'
import { Link } from 'react-router-dom'

export function Register() {
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [passwordStrength, setPasswordStrength] = useState(0)
    const [passwordFeedback, setPasswordFeedback] = useState('')

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

    const handleSubmit = (e) => {
        e.preventDefault()
        // Handle register logic here
        console.log('Register:', { username, email, password })
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
            <h1 className="text-2xl font-bold text-[rgb(77,76,76)] dark:text-zinc-100 mb-8">
                Regístrate
            </h1>

            {/* Form */}
            <form onSubmit={handleSubmit} className="w-full max-w-[400px] space-y-4">
                <input
                    type="text"
                    placeholder="Nombre de usuario"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full h-[45px] px-4 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors"
                />

                <input
                    type="email"
                    placeholder="Correo electrónico"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
                    disabled={passwordStrength < 3}
                    className={`w-full h-[45px] text-white text-base font-bold transition-colors mt-4 ${passwordStrength < 3
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-[rgb(169,191,162)] hover:bg-[rgb(159,181,152)]'
                        }`}
                >
                    Crear cuenta
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
