import { useState, useEffect } from 'react'
import { obtenerClienteLocal, ClienteService } from '../../services/apiservice'

export function GeneralProfile() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadUser()
    }, [])

    const loadUser = async () => {
        try {
            const localUser = obtenerClienteLocal()
            if (localUser?.id_cliente) {
                // Try to get fresh data
                try {
                    const freshData = await ClienteService.obtener(localUser.id_cliente)
                    setUser(freshData)
                } catch (e) {
                    console.error("Error fetching fresh user data, using local", e)
                    setUser(localUser)
                }
            }
        } catch (error) {
            console.error('Error loading user:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Cargando información...</div>
    }

    if (!user) {
        return <div className="p-8 text-center text-gray-500">No has iniciado sesión.</div>
    }

    return (
        <div className="bg-white dark:bg-zinc-900 p-6 sm:p-8 w-full max-w-2xl">
            <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-100 mb-6">Información General</h2>
            
            <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-500 dark:text-zinc-400 mb-1">
                            Nombre
                        </label>
                        <p className="text-base text-gray-900 dark:text-zinc-100 font-normal">
                            {user.nombre} {user.apellido}
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-500 dark:text-zinc-400 mb-1">
                            Correo Electrónico
                        </label>
                        <p className="text-base text-gray-900 dark:text-zinc-100 font-normal">
                            {user.correo}
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-500 dark:text-zinc-400 mb-1">
                            Teléfono
                        </label>
                        <p className="text-base text-gray-900 dark:text-zinc-100 font-normal">
                            {user.telefono || 'No registrado'}
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-500 dark:text-zinc-400 mb-1">
                            Fecha de Registro
                        </label>
                        <p className="text-base text-gray-900 dark:text-zinc-100 font-normal">
                            {user.fecha_registro ? new Date(user.fecha_registro).toLocaleDateString() : 'N/A'}
                        </p>
                    </div>
                </div>

                <div className="pt-6 border-t border-gray-100 dark:border-zinc-800">
                    <button className="text-sm text-[rgb(169,191,162)] hover:underline font-medium">
                        Editar información
                    </button>
                </div>
            </div>
        </div>
    )
}
