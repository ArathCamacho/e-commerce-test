import { useState } from 'react'
import { useCart } from '../../context/CartContext'
import { useCheckout } from '../../context/CheckoutContext'
import { useNavigate } from 'react-router-dom'
import {
    PagoService,
    PedidoService,
    obtenerClienteLocal
} from '../../services/apiservice'

export function CheckoutSummary() {
    const { cartTotal, cart, clearCart, showNotification } = useCart()
    const { address, paymentMethod, savePaymentMethod, openAddressModal, openPaymentModal } = useCheckout()
    const navigate = useNavigate()
    
    const shippingCost = 140.00
    const total = cartTotal // Envío gratis

    const [loading, setLoading] = useState(false)
    const [paymentStatus, setPaymentStatus] = useState(null) // 'processing', 'success', 'error'

    const handlePurchase = async () => {
        try {
            setLoading(true)
            setPaymentStatus('processing')

            const cliente = obtenerClienteLocal()
            if (!cliente?.id_cliente) {
                showNotification("Debes iniciar sesión para completar la compra", "error")
                setPaymentStatus('error')
                setLoading(false)
                return
            }

            const direccionAUsar = address.id_direccion || 1

            console.log('🛒 Iniciando proceso de compra...')
            console.log('📍 Dirección:', address)
            console.log('💰 Total:', total)

            // ========================================
            // PASO 1: Crear el pedido desde el carrito
            // ========================================
            console.log('📦 Creando pedido...')
            const pedidoResponse = await PedidoService.crear(
                cliente.id_cliente,
                direccionAUsar
            )
            console.log('✅ Pedido creado:', pedidoResponse)

            // ========================================
            // PASO 2: Procesar el pago con el banco
            // ========================================
            if (!paymentMethod) {
                showNotification("No se encontró método de pago. Por favor añade uno.", "error")
                setPaymentStatus('error')
                setLoading(false)
                return
            }

            const numeroTarjeta = paymentMethod.cardNumber?.replace(/\s/g, '') || "5555555555554444"
            const [mesExp, anioExp] = paymentMethod.expiryDate?.split('/') || ['12', '30']

            const datosPago = {
                id_pedido: pedidoResponse.id_pedido,
                numero_tarjeta_origen: numeroTarjeta,
                nombre_cliente: paymentMethod.cardholderName || cliente.nombre || "Cliente",
                mes_exp: parseInt(mesExp) || 12,
                anio_exp: parseInt(`20${anioExp}`) || 2030,
                cvv: paymentMethod.cvv || "111",
                monto: parseFloat(pedidoResponse.total),
                moneda: "MXN",
                tipo: "venta"
            }

            console.log('💳 Procesando pago con banco...')
            const pagoResponse = await PagoService.procesar(datosPago)
            console.log('💰 Respuesta del pago:', pagoResponse)

            const estadoPago = pagoResponse.estado?.toUpperCase()

            // ========================================
            // PASO 3: Verificar resultado del pago
            // ========================================
            if (estadoPago === "APROBADO" || estadoPago === "COMPLETADO") {
                
                console.log('✅ Pago exitoso!')
                console.log('📦 El backend está creando el envío automáticamente...')

                // ✨ YA NO CREAMOS EL ENVÍO MANUALMENTE
                // El backend lo hace automáticamente en PagoServices._crear_envio_automatico()
                
                setPaymentStatus('success')
                showNotification(
                    "¡Compra exitosa! Tu pedido y envío han sido procesados.", 
                    "success"
                )

                // Limpiar carrito
                await clearCart()

                // Redirigir a pedidos
                setTimeout(() => {
                    navigate('/account?tab=orders')
                }, 2000)

            } else if (estadoPago === "RECHAZADO") {
                setPaymentStatus('error')
                console.error('❌ Pago rechazado:', pagoResponse)
                showNotification(
                    `Pago rechazado: ${pagoResponse.mensaje || 'Verifica los datos de tu tarjeta'}`,
                    "error"
                )
            } else {
                setPaymentStatus('error')
                showNotification(
                    `Estado del pago: ${estadoPago}. ${pagoResponse.mensaje || ''}`,
                    "warning"
                )
            }

        } catch (error) {
            console.error('💥 Error en el proceso de compra:', error)
            setPaymentStatus('error')
            
            const errorMsg = error.response?.data?.detail || error.message || 'Error al procesar la compra'
            showNotification(errorMsg, "error")
            
        } finally {
            setLoading(false)
            setTimeout(() => setPaymentStatus(null), 3000)
        }
    }

    const handleContinue = () => {
        console.log('Validando dirección:', address)
        console.log('Validando método de pago:', paymentMethod)

        // Validar dirección - permitir direcciones temporales (sin id_direccion)
        if (!address || !address.street || !address.city || !address.zipCode) {
            console.log('Dirección inválida, abriendo modal')
            openAddressModal()
            showNotification("Por favor completa tu dirección de envío", "error")
            return
        }

        // Validar método de pago
        if (!paymentMethod) {
            console.log('Método de pago faltante, abriendo modal')
            openPaymentModal()
            showNotification("Por favor selecciona un método de pago", "error")
            return
        }

        console.log('Validaciones pasaron, procediendo con el pago')
        // Si todo está validado, proceder con el pago
        handlePurchase()
    }

    return (
        <>
            <div className="lg:sticky lg:top-24 h-fit">
                {/* Discounts Section */}
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase">
                            DESCUENTOS
                        </h2>
                        <button className="text-sm font-bold text-gray-900 dark:text-zinc-100 uppercase hover:text-gray-600 dark:hover:text-zinc-400 transition-colors">
                            AGREGAR
                        </button>
                    </div>
                </div>

                {/* Order Summary */}
                <div className="space-y-3 mb-6 text-sm">
                    <div className="flex justify-between text-gray-700 dark:text-zinc-300">
                        <span>Valor del pedido</span>
                        <span>${cartTotal.toFixed(2)}</span>
                    </div>
                {/* Envío gratis */}
                {/* <div className="flex justify-between text-gray-700 dark:text-zinc-300">
                    <span>Costo estimado de envío</span>
                    <span>${shippingCost.toFixed(2)}</span>
                </div> */}
                </div>

                {/* Total */}
                <div className="flex justify-between text-base font-bold text-gray-900 dark:text-zinc-100 mb-6 pb-6 border-b border-gray-200 dark:border-zinc-800">
                    <span>TOTAL</span>
                    <span>${total.toFixed(2)}</span>
                </div>

                {/* Payment Status Messages */}
                {paymentStatus === 'processing' && (
                    <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                        <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                            <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span className="font-medium">Procesando pago y creando envío...</span>
                        </div>
                    </div>
                )}

                {paymentStatus === 'success' && (
                    <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                        <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="font-medium">¡Compra exitosa! Redirigiendo...</span>
                        </div>
                    </div>
                )}

                {paymentStatus === 'error' && (
                    <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
                            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span className="font-medium">Error en la compra</span>
                        </div>
                    </div>
                )}

                {/* Checkout Button */}
                <button
                    onClick={handleContinue}
                    disabled={loading || cartTotal === 0}
                    className={`w-full py-4 px-6 font-bold text-sm uppercase transition-colors mb-6 ${
                        loading || cartTotal === 0
                            ? 'bg-gray-400 dark:bg-zinc-700 text-gray-200 dark:text-zinc-500 cursor-not-allowed'
                            : paymentMethod
                            ? 'bg-black dark:bg-white text-white dark:text-black hover:bg-gray-900 dark:hover:bg-zinc-200'
                            : 'bg-gray-900 dark:bg-zinc-700 text-white hover:bg-black dark:hover:bg-zinc-600'
                    }`}
                >
                    {loading
                        ? 'PROCESANDO...'
                        : 'CONTINUAR CON EL PAGO'
                    }
                </button>

                {/* Payment Info */}
                <div className="text-xs text-gray-500 dark:text-zinc-500 text-center mb-4">
                    Pago seguro procesado por el banco
                </div>

                {/* Payment Methods - Removido por seguridad */}
            </div>

        </>
    )
}