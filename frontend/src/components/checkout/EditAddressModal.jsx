import { useState, useEffect } from 'react'
import { Modal } from '../common/Modal'

export function EditAddressModal({ isOpen, onClose, onSave, initialData }) {
    const [formData, setFormData] = useState({
        street: initialData?.street || '',
        city: initialData?.city || '',
        zipCode: initialData?.zipCode || '',
        state: initialData?.state || '',
        country: initialData?.country || ''
    })
    const [errors, setErrors] = useState({})

    useEffect(() => {
        if (isOpen) {
            setFormData({
                street: initialData?.street || '',
                city: initialData?.city || '',
                zipCode: initialData?.zipCode || '',
                state: initialData?.state || '',
                country: initialData?.country || ''
            })
            setErrors({})
        }
    }, [isOpen, initialData])

    const validateForm = () => {
        const newErrors = {}

        if (!formData.street.trim()) {
            newErrors.street = 'La calle es requerida'
        }

        if (!formData.city.trim()) {
            newErrors.city = 'La ciudad es requerida'
        }

        if (!formData.state.trim()) {
            newErrors.state = 'El estado es requerido'
        }

        if (!formData.zipCode.trim()) {
            newErrors.zipCode = 'El código postal es requerido'
        } else if (!/^\d{5}$/.test(formData.zipCode)) {
            newErrors.zipCode = 'El código postal debe tener 5 dígitos'
        }

        if (!formData.country.trim()) {
            newErrors.country = 'El país es requerido'
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
        <Modal isOpen={isOpen} onClose={onClose} title="Editar Dirección de Facturación">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                        Calle y Número
                    </label>
                    <input
                        type="text"
                        value={formData.street}
                        onChange={(e) => handleChange('street', e.target.value)}
                        className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.street ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                            } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                        placeholder="Av. Principal #123"
                    />
                    {errors.street && <p className="mt-1 text-sm text-red-500">{errors.street}</p>}
                </div>

                <div className="grid grid-cols-3 gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                            Código Postal
                        </label>
                        <input
                            type="text"
                            value={formData.zipCode}
                            onChange={(e) => handleChange('zipCode', e.target.value)}
                            maxLength={5}
                            className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.zipCode ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                                } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                            placeholder="12345"
                        />
                        {errors.zipCode && <p className="mt-1 text-sm text-red-500">{errors.zipCode}</p>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                            Ciudad
                        </label>
                        <input
                            type="text"
                            value={formData.city}
                            onChange={(e) => handleChange('city', e.target.value)}
                            className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.city ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                                } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                            placeholder="Hermosillo"
                        />
                        {errors.city && <p className="mt-1 text-sm text-red-500">{errors.city}</p>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                            Estado
                        </label>
                        <input
                            type="text"
                            value={formData.state}
                            onChange={(e) => handleChange('state', e.target.value)}
                            className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.state ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                                } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                            placeholder="Sonora"
                        />
                        {errors.state && <p className="mt-1 text-sm text-red-500">{errors.state}</p>}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-zinc-100 mb-2 uppercase">
                        País
                    </label>
                    <input
                        type="text"
                        value={formData.country}
                        onChange={(e) => handleChange('country', e.target.value)}
                        className={`w-full px-4 py-3 bg-white dark:bg-zinc-900 border ${errors.country ? 'border-red-500' : 'border-gray-300 dark:border-zinc-700'
                            } text-gray-900 dark:text-zinc-100 focus:outline-none focus:border-black dark:focus:border-white transition-colors`}
                        placeholder="México"
                    />
                    {errors.country && <p className="mt-1 text-sm text-red-500">{errors.country}</p>}
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
