import { createContext, useContext, useState, useEffect } from 'react'
import { DireccionService, obtenerClienteLocal } from '../services/apiservice'

const CheckoutContext = createContext()

export function CheckoutProvider({ children }) {
    const [userInfo, setUserInfo] = useState({
        name: '',
        email: ''
    })

    const [address, setAddress] = useState({
        id_direccion: null,
        street: 'Calle Siempre viva #54',
        zipCode: '83125',
        city: 'Hermosillo',
        country: 'México'
    })

    const [shipping, setShipping] = useState({
        name: '',
        phone: '+52 662 154 5465'
    })

    const [paymentMethod, setPaymentMethod] = useState(null)

    // Cargar información del cliente al montar
    useEffect(() => {
        loadClienteInfo()
        loadDirecciones()
    }, [])

    const loadClienteInfo = () => {
        const cliente = obtenerClienteLocal()
        if (cliente) {
            const fullName = `${cliente.nombre || ''} ${cliente.apellido || ''}`.trim()
            setUserInfo({
                name: fullName,
                email: cliente.correo || ''
            })
            setShipping(prev => ({
                ...prev,
                name: fullName
            }))
        }
    }

    const loadDirecciones = async () => {
        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) return

            const direcciones = await DireccionService.obtener(cliente.id_cliente)
            
            // Si hay direcciones, usar la primera como predeterminada
            if (direcciones && direcciones.length > 0) {
                const dir = direcciones[0]
                setAddress({
                    id_direccion: dir.id_direccion,
                    street: dir.calle,
                    zipCode: dir.codigo_postal,
                    city: dir.ciudad,
                    country: dir.estado || 'México'
                })
            }
        } catch (error) {
            console.error('Error cargando direcciones:', error)
        }
    }

    const updateUserInfo = (newInfo) => {
        setUserInfo(newInfo)
    }

    const updateAddress = (newAddress) => {
        setAddress(newAddress)
    }

    const updateShipping = (newShipping) => {
        setShipping(newShipping)
    }

    const savePaymentMethod = (paymentData) => {
        setPaymentMethod(paymentData)
    }

    return (
        <CheckoutContext.Provider
            value={{
                userInfo,
                address,
                shipping,
                paymentMethod,
                updateUserInfo,
                updateAddress,
                updateShipping,
                savePaymentMethod,
                loadDirecciones
            }}
        >
            {children}
        </CheckoutContext.Provider>
    )
}

export function useCheckout() {
    const context = useContext(CheckoutContext)
    if (!context) {
        throw new Error('useCheckout must be used within a CheckoutProvider')
    }
    return context
}