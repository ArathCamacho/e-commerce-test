import { useState, useEffect } from 'react'
import { Modal } from './Modal'

export function EditInfoModal({ isOpen, onClose, onSave, initialData }) {
    const [formData, setFormData] = useState({
        name: initialData?.name || '',
        email: initialData?.email || ''
    })
    const [errors, setErrors] = useState({})

    // Reset form when modal opens/closes
    useEffect(() => {
        if (isOpen) {
            setFormData({
                name: initialData?.name || '',
                email: initialData?.email || ''
            })
            setErrors({})
        }
    }, [isOpen, initialData])

    const validateForm = () => {
        const newErrors = {}

        if (!formData.name.trim()) {
            newErrors.name = 'El nombre es requerido'
        }

        if (!formData.email.trim()) {
            newErrors.email = 'El correo electrónico es requerido'
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = 'El correo electrónico no es válido'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (validateForm()) {
            onSave(formData)
            onClose()
        }
    }

    const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }))
        if (errors[field]) {
            setErrors(prev => ({ ...prev, [field]: '' }))
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Editar Información">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                        Nombre Completo
                    </label>
                    <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleChange('name', e.target.value)}
                        className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.name ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                            } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                        placeholder="Juan Pérez García"
                    />
                    {errors.name && <p className="mt-1 text-sm text-red-500">{errors.name}</p>}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                        Correo Electrónico
                    </label>
                    <input
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleChange('email', e.target.value)}
                        className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.email ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                            } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                        placeholder="ejemplo@correo.com"
                    />
                    {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
                </div>

                <div className="flex gap-3 pt-4">
                    <button
                        type="button"
                        onClick={onClose}
                        className="flex-1 px-4 py-3 border border-gray-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-gray-900 dark:text-zinc-100 font-medium uppercase hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        className="flex-1 px-4 py-3 bg-black dark:bg-white text-white dark:text-black font-medium uppercase hover:bg-gray-900 dark:hover:bg-zinc-200 transition-colors"
                    >
                        Guardar
                    </button>
                </div>
            </form>
        </Modal>
    )
}
