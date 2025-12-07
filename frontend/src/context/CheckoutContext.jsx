import { createContext, useContext, useState, useEffect } from 'react'
import { DireccionService, obtenerClienteLocal } from '../services/apiservice'

const CheckoutContext = createContext()

export function CheckoutProvider({ children }) {
    const [userInfo, setUserInfo] = useState({
        name: '',
        email: '',
        phone: ''
    })

    const [address, setAddress] = useState({
        id_direccion: null,
        street: 'Calle Siempre viva #54',
        zipCode: '83125',
        city: 'Hermosillo',
        country: 'México'
    })

    const [paymentMethod, setPaymentMethod] = useState(null)

    // Estados para controlar modales
    const [showAddressModal, setShowAddressModal] = useState(false)
    const [showPaymentModal, setShowPaymentModal] = useState(false)

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
                email: cliente.correo || '',
                phone: cliente.telefono || ''
            })
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
                    state: dir.estado,
                    country: 'México' // Hardcodeado por ahora
                })
            }
        } catch (error) {
            console.error('Error cargando direcciones:', error)
        }
    }

    const updateUserInfo = (newInfo) => {
        setUserInfo(newInfo)
    }

    const updateAddress = async (newAddress) => {
        try {
            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                setAddress(newAddress)
                return
            }

            // Si la dirección editada no tiene id_direccion, guardarla como nueva dirección
            if (!newAddress.id_direccion) {
                const direccionData = {
                    calle: newAddress.street,
                    ciudad: newAddress.city,
                    codigo_postal: newAddress.zipCode,
                    estado: newAddress.state || 'Sonora', // Default state if not provided
                    referencias: `Dirección de envío - ${new Date().toLocaleDateString()}`
                }

                const nuevaDireccion = await DireccionService.agregar(cliente.id_cliente, direccionData)
                console.log('Nueva dirección guardada:', nuevaDireccion)

                // Actualizar el estado con la dirección guardada
                const updatedAddress = {
                    id_direccion: nuevaDireccion.id_direccion,
                    street: nuevaDireccion.calle,
                    zipCode: nuevaDireccion.codigo_postal,
                    city: nuevaDireccion.ciudad,
                    state: nuevaDireccion.estado,
                    country: 'México'
                }
                setAddress(updatedAddress)
                console.log('Estado de dirección actualizado:', updatedAddress)
            } else {
                // Si ya tiene id_direccion, solo actualizar el estado
                setAddress(newAddress)
            }
        } catch (error) {
            console.error('Error updating address:', error)
            // En caso de error, actualizar el estado local de todas formas
            setAddress(newAddress)
        }
    }

    const savePaymentMethod = (paymentData) => {
        setPaymentMethod(paymentData)
    }

    const openAddressModal = () => setShowAddressModal(true)
    const closeAddressModal = () => setShowAddressModal(false)

    const openPaymentModal = () => setShowPaymentModal(true)
    const closePaymentModal = () => setShowPaymentModal(false)

    return (
        <CheckoutContext.Provider
            value={{
                userInfo,
                address,
                paymentMethod,
                updateUserInfo,
                updateAddress,
                savePaymentMethod,
                loadDirecciones,
                showAddressModal,
                showPaymentModal,
                openAddressModal,
                closeAddressModal,
                openPaymentModal,
                closePaymentModal
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