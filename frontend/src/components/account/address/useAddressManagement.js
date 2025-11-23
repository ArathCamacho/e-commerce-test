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
    const deleteAddress = (id) => {
        setAddresses(prev => {
            const filtered = prev.filter(addr => addr.id !== id)

            // If we deleted the default address and there are others, make the first one default
            const deletedWasDefault = prev.find(addr => addr.id === id)?.isDefault
            if (deletedWasDefault && filtered.length > 0) {
                filtered[0].isDefault = true
            }

            return filtered
        })
    }

    /**
     * Set an address as default
     */
    const setDefaultAddress = (id) => {
        setAddresses(prev => prev.map(addr => ({
            ...addr,
            isDefault: addr.id === id
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
        getDefaultAddress
    }
}
