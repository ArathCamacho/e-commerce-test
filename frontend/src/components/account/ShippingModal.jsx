import { useState, useEffect } from 'react'
import { EnvioService } from '../../services/apiservice'
import { Modal } from '../common/Modal'

export function ShippingModal({ isOpen, onClose, pedido, cliente }) {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(null)
    const [envio, setEnvio] = useState(null)
    const [checkingExisting, setCheckingExisting] = useState(true)

    // Datos del cliente para el envío (sin dirección)
    const [datosCliente, setDatosCliente] = useState({
        nombre: cliente?.nombre || pedido?.fullData?.cliente?.nombre || '',
        telefono: cliente?.telefono || pedido?.fullData?.cliente?.telefono || '',
        email: cliente?.correo || pedido?.fullData?.cliente?.correo || '',
        pais: 'México'
    })


    // Actualizar datos del cliente cuando cambien las props
    useEffect(() => {
        if (cliente || pedido) {
            setDatosCliente({
                nombre: cliente?.nombre || '',
                telefono: cliente?.telefono || '',
                email: cliente?.correo || '',
                pais: 'México'
            })
        }
    }, [cliente, pedido])

    // Verificar si ya existe un envío para este pedido
    useEffect(() => {
        if (isOpen && pedido?.id) {
            verificarEnvioExistente()
        }
    }, [isOpen, pedido])

    const verificarEnvioExistente = async () => {
        try {
            setCheckingExisting(true)
            const envioExistente = await EnvioService.consultarPorPedido(pedido.id)
            setEnvio(envioExistente)
        } catch (err) {
            // Si no existe, no es un error - simplemente no hay envío
            console.log('No hay envío existente para este pedido')
            setEnvio(null)
        } finally {
            setCheckingExisting(false)
        }
    }

    const crearEnvio = async () => {
        setLoading(true)
        setError(null)
        setSuccess(null)

        try {
            // Generar ID único para la orden externa
            const timestamp = Date.now()
            const idOrdenExterna = `ECM-${timestamp}`

            // Preparar productos del pedido
            const productos = pedido.fullData?.items?.map(item => ({
                sku: `SKU-${item.producto?.id_producto || item.id_producto}`,
                nombre: item.producto?.nombre || 'Producto',
                cantidad: item.cantidad || 1,
                precio_unitario: item.precio_unitario || 0
            })) || [
                {
                    sku: `PEDIDO-${pedido.id}`,
                    nombre: pedido.title || `Pedido #${pedido.id}`,
                    cantidad: 1,
                    precio_unitario: parseFloat(pedido.total?.replace('$', '')) || 0
                }
            ]

            // Crear solicitud de envío
            const solicitudEnvio = {
                id_orden_externa: idOrdenExterna,
                id_orden_original: `P-${pedido.id}`,
                servicio_origen: "ecommerce",
                webhook_url: "https://e-commerce-test-mm6o.onrender.com/api/envios/webhook",
                datos_cliente: datosCliente,
                productos: productos
            }

            console.log('Creando envío:', solicitudEnvio)

            const nuevoEnvio = await EnvioService.crear(solicitudEnvio)
            
            setEnvio(nuevoEnvio)
            setSuccess('✅ Envío creado exitosamente')

        } catch (err) {
            console.error('Error al crear envío:', err)
            setError(err.response?.data?.detail || err.message || 'Error al crear el envío')
        } finally {
            setLoading(false)
        }
    }

    const actualizarEstado = async () => {
        if (!envio?.id_envio) return

        try {
            setLoading(true)
            const envioActualizado = await EnvioService.consultar(envio.id_envio)
            setEnvio(envioActualizado)
            setSuccess('Estado actualizado')
        } catch (err) {
            setError('Error al actualizar estado')
        } finally {
            setLoading(false)
        }
    }

    const getEstadoColor = (estado) => {
        const colores = {
            'PENDIENTE': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
            'Solicitud Recibida': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
            'EN_PREPARACION': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
            'Fecha de Envío Establecida': 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
            'EN_TRANSITO': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
            'ENTREGADO': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
            'ERROR': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }
        return colores[estado] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }

    return (
        <Modal 
            isOpen={isOpen} 
            onClose={onClose}
            title="Información de Envío"
            width="650px"
        >
            {/* Alertas */}
            {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
                    <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                </div>
            )}

            {success && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 mb-4">
                    <p className="text-green-800 dark:text-green-200 text-sm">{success}</p>
                </div>
            )}

            {/* Loading state */}
            {checkingExisting ? (
                <div className="text-center py-8">
                    <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                    <p className="mt-2 text-gray-600 dark:text-zinc-400">Verificando envío...</p>
                </div>
            ) : envio ? (
                /* Ya existe un envío */
                <div className="space-y-4">
                    <div className="bg-gray-50 dark:bg-zinc-800 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="font-semibold text-black dark:text-zinc-100">
                                {envio.codigo_seguimiento}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEstadoColor(envio.estado_actual)}`}>
                                {envio.estado_actual}
                            </span>
                        </div>

                        <div className="space-y-3 text-sm">
                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                                <div>
                                    <p className="text-gray-600 dark:text-zinc-400 font-medium">Ubicación:</p>
                                    <p className="text-gray-800 dark:text-zinc-200">
                                        {envio.ubicacion_actual || 'Sin información'}
                                    </p>
                                </div>
                            </div>

                            {envio.fecha_actualizacion && (
                                <div className="flex items-start gap-2">
                                    <svg className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                        <p className="text-gray-600 dark:text-zinc-400 font-medium">Última actualización:</p>
                                        <p className="text-gray-800 dark:text-zinc-200">
                                            {new Date(envio.fecha_actualizacion).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            )}

                            <div className="flex items-start gap-2">
                                <svg className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                                </svg>
                                <div>
                                    <p className="text-gray-600 dark:text-zinc-400 font-medium">ID Orden:</p>
                                    <p className="text-gray-800 dark:text-zinc-200">
                                        {envio.id_orden_externa}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={actualizarEstado}
                        disabled={loading}
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? 'Actualizando...' : 'Actualizar Estado'}
                    </button>
                </div>
            ) : (
                /* No existe envío - permitir crearlo */
                <div className="space-y-4">
                    {/* Información del cliente (solo lectura) */}
                    <div className="space-y-3">
                        <h4 className="font-medium text-black dark:text-zinc-100">
                            Datos de Envío
                        </h4>

                        <div className="text-sm text-gray-700 dark:text-zinc-300 space-y-2">
                            <p><strong>Nombre:</strong> {datosCliente.nombre}</p>
                            <p><strong>Teléfono:</strong> {datosCliente.telefono}</p>
                            <p><strong>Email:</strong> {datosCliente.email}</p>
                        </div>
                    </div>

                    {/* Información del pedido */}
                    <div className="bg-gray-50 dark:bg-zinc-800 rounded-lg p-4">
                        <h3 className="font-semibold text-black dark:text-zinc-100 mb-2">
                            Pedido #{pedido.id}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-zinc-400">
                            Total: {pedido.total}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-zinc-400">
                            Estado: {pedido.status}
                        </p>
                    </div>

                    <button
                        onClick={() => {/* TODO: Implementar edición de datos de envío */}}
                        className="w-full bg-[rgb(169,191,162)] text-white py-3 px-4 rounded font-medium hover:bg-[rgb(159,181,152)] transition-colors"
                    >
                        Editar datos de envío
                    </button>
                </div>
            )}
        </Modal>
    )
}