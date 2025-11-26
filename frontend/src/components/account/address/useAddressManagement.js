import { useState } from 'react'

/**
 * Custom hook for managing addresses
 * Handles all CRUD operations and state management for addresses
 */
export function useAddressManagement(initialAddresses = []) {
    const [addresses, setAddresses] = useState(initialAddresses)

    /**
     * Add a new address
     */
    const addAddress = (addressData) => {
        const newId = Math.max(...addresses.map(a => a.id), 0) + 1
        const newAddress = {
            ...addressData,
            id: newId,
            isDefault: addresses.length === 0 // First address is default
        }
        setAddresses(prev => [...prev, newAddress])
        return newAddress
    }

    /**
     * Update an existing address
     */
    const updateAddress = (id, addressData) => {
        setAddresses(prev => prev.map(addr =>
            addr.id === id ? { ...addr, ...addressData } : addr
        ))
    }

    /**
     * Delete an address
     */
    /**
     * Delete an address
     */
    const deleteAddress = (id) => {
        setAddresses(prev => prev.filter(addr => addr.id !== id))
    }

    /**
     * Set an address as default
     * If id is null, unsets all defaults
     */
    const setDefaultAddress = (id) => {
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
        addAddress,
        updateAddress,
        deleteAddress,
        setDefaultAddress,
        getAddressById,
        getDefaultAddress,
        unsetDefaultAddress
    }
}
