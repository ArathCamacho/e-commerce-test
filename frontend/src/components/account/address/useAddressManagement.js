import { useState, useEffect } from 'react'
import { DireccionService, obtenerClienteLocal } from '../../../services/apiservice'

/**
 * Custom hook for managing addresses
 * Handles all CRUD operations and state management for addresses
 */
export function useAddressManagement() {
    const [addresses, setAddresses] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadAddresses()
    }, [])

    const loadAddresses = async () => {
        try {
            setLoading(true)
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                setAddresses([])
                return
            }
            const response = await DireccionService.obtener(cliente.id_cliente)
            // Adapt backend response to frontend model if needed
            // Assuming response is a list of addresses
            const adaptedAddresses = (response.direcciones || response || []).map(addr => ({
                id: addr.id_direccion || addr.id,
                name: addr.nombre_completo || 'Usuario', // Backend might not have this, use fallback
                phone: addr.telefono || '',
                street: addr.calle || '',
                details: `${addr.calle} #${addr.numero_exterior} ${addr.numero_interior ? 'Int ' + addr.numero_interior : ''}, ${addr.colonia}`,
                city: `${addr.ciudad}, ${addr.estado}, ${addr.pais}`,
                postalCode: addr.codigo_postal || '',
                isDefault: addr.es_principal || false,
                // Keep original data for updates
                originalData: addr
            }))
            setAddresses(adaptedAddresses)
        } catch (err) {
            console.error('Error loading addresses:', err)
            setError('Error al cargar direcciones')
        } finally {
            setLoading(false)
        }
    }

    /**
     * Add a new address
     */
    const addAddress = async (addressData) => {
        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) return

            // Adapt frontend data to backend schema
            const backendData = {
                calle: addressData.street,
                numero_exterior: "S/N", // Frontend form might need this field
                numero_interior: "",
                colonia: "", // Frontend form might need this field
                ciudad: addressData.city.split(',')[0].trim(), // Rough parsing
                estado: "", 
                codigo_postal: addressData.postalCode,
                pais: "México",
                telefono: addressData.phone,
                es_principal: addresses.length === 0
            }

            // Note: The current AddressFormModal might not have all fields required by backend.
            // For now, we'll try to map what we have.
            
            await DireccionService.agregar(cliente.id_cliente, backendData)
            await loadAddresses()
        } catch (err) {
            console.error('Error adding address:', err)
            setError('Error al agregar dirección')
        }
    }

    /**
     * Update an existing address
     */
    const updateAddress = async (id, addressData) => {
        // Backend update not implemented in DireccionService yet?
        // Checking apiservice.js... DireccionService only has agregar and obtener.
        // We might need to implement update in service if backend supports it.
        // For now, we'll just update local state or log warning.
        console.warn("Update address not fully implemented in backend service")
    }

    /**
     * Delete an address
     */
    const deleteAddress = async (id) => {
        // Backend delete not implemented in DireccionService yet?
        console.warn("Delete address not fully implemented in backend service")
    }

    /**
     * Set an address as default
     */
    const setDefaultAddress = async (id) => {
        // Backend set default not implemented?
        // Optimistic update
        setAddresses(prev => prev.map(addr => ({
            ...addr,
            isDefault: addr.id === id
        })))
    }

    /**
     * Unset default address
     */
    const unsetDefaultAddress = () => {
        setAddresses(prev => prev.map(addr => ({
            ...addr,
            isDefault: false
        })))
    }

    /**
     * Get address by ID
     */
    const getAddressById = (id) => {
        return addresses.find(addr => addr.id === id)
    }

    /**
     * Get default address
     */
    const getDefaultAddress = () => {
        return addresses.find(addr => addr.isDefault)
    }

    return {
        addresses,
        loading,
        error,
        addAddress,
        updateAddress,
        deleteAddress,
        setDefaultAddress,
        getAddressById,
        getDefaultAddress,
        unsetDefaultAddress
    }
}
