import { useState, useEffect } from 'react'
import { obtenerClienteLocal, ClienteService, guardarClienteLocal } from '../../services/apiservice'
import { EditInfoModal } from '../checkout/EditInfoModal'

export function GeneralProfile() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [showEditModal, setShowEditModal] = useState(false)

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

    const handleEditInfo = async (formData) => {
        try {
            // Separar nombre completo en nombre y apellido
            const nameParts = formData.name.trim().split(' ')
            const nombre = nameParts[0] || ''
            const apellido = nameParts.slice(1).join(' ') || ''

            const updateData = {
                nombre: nombre,
                apellido: apellido,
                correo: formData.email,
                telefono: formData.telefono
            }

            await ClienteService.actualizar(user.id_cliente, updateData)

            // Reload user data
            await loadUser()

            // Update local storage
            const updatedUser = { ...user, ...updateData }
            localStorage.setItem('cliente', JSON.stringify(updatedUser))

        } catch (error) {
            console.error('Error updating user info:', error)
            alert('Error al actualizar la información. Por favor intenta de nuevo.')
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
                    <button
                        onClick={() => setShowEditModal(true)}
                        className="text-sm text-[rgb(169,191,162)] hover:underline font-medium"
                    >
                        Editar información
                    </button>
                </div>
            </div>

            {/* Edit Info Modal */}
            <EditInfoModal
                isOpen={showEditModal}
                onClose={() => setShowEditModal(false)}
                onSave={handleEditInfo}
                initialData={{
                    name: user ? `${user.nombre} ${user.apellido}` : '',
                    email: user?.correo || '',
                    telefono: user?.telefono || ''
                }}
            />
        </div>
    )
}
