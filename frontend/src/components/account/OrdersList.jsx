import { useState, useEffect } from 'react'
import { PedidoService, obtenerClienteLocal, ClienteService } from '../../services/apiservice'
import { Modal } from '../common/Modal'

export function OrdersList({ filterStatus = 'all', timeFilter = 'last-year' }) {
    const [allOrders, setAllOrders] = useState([])
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedOrder, setSelectedOrder] = useState(null)
    const [cliente, setCliente] = useState(null)
    const [showDetailsModal, setShowDetailsModal] = useState(false)
    const [selectedOrderDetails, setSelectedOrderDetails] = useState(null)
    const [orderDetailData, setOrderDetailData] = useState(null)
    const [loadingDetail, setLoadingDetail] = useState(false)

    useEffect(() => {
        const loadClienteData = async () => {
            const clienteData = obtenerClienteLocal()
            if (clienteData?.id_cliente) {
                try {
                    // Obtener información completa del cliente desde el backend
                    const clienteCompleto = await ClienteService.obtener(clienteData.id_cliente)
                    setCliente(clienteCompleto)
                } catch (error) {
                    console.error('Error obteniendo cliente:', error)
                    setCliente(clienteData) // Usar datos básicos como fallback
                }
            }
            loadOrders()
        }

        loadClienteData()
    }, [])

    // Aplicar filtros cuando cambien
    useEffect(() => {
        applyFilters()
    }, [allOrders, filterStatus, timeFilter])

    const applyFilters = () => {
        let filteredOrders = [...allOrders]

        // Filtrar por estado
        if (filterStatus !== 'all') {
            const statusMapping = {
                'pending': ['PENDIENTE'],
                'shipping': ['PAGADO', 'EN_PREPARACION'],
                'shipped': ['ENVIADO'],
                'processed': ['ENTREGADO', 'CANCELADO']
            }

            const allowedStatuses = statusMapping[filterStatus] || []
            filteredOrders = filteredOrders.filter(order =>
                allowedStatuses.includes(order.status)
            )
        }

        // Filtrar por tiempo
        if (timeFilter !== 'last-year') {
            const now = new Date()
            let cutoffDate

            switch (timeFilter) {
                case 'last-month':
                    cutoffDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate())
                    break
                case 'last-week':
                    cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
                    break
                default:
                    cutoffDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())
            }

            filteredOrders = filteredOrders.filter(order => {
                const orderDate = new Date(order.fullData?.fecha_creacion || order.details?.split('Fecha: ')[1])
                return orderDate >= cutoffDate
            })
        }

        setOrders(filteredOrders)
    }

    const loadOrders = async () => {
        try {
            setLoading(true)
            const cliente = obtenerClienteLocal()
            
            if (!cliente?.id_cliente) {
                setOrders([])
                setError('Debes iniciar sesión para ver tus pedidos')
                return
            }
            
            const response = await PedidoService.listarPorCliente(cliente.id_cliente)
            const rawOrders = response.pedidos || response || []

            // Map backend data to UI format
            const mappedOrders = rawOrders.map(order => {
                const firstItem = order.items && order.items.length > 0 ? order.items[0] : null
                const product = firstItem ? firstItem.producto : null

                return {
                    id: order.id_pedido,
                    status: order.estado,
                    statusKey: order.estado ? order.estado.toLowerCase() : 'pending',
                    title: product ? product.nombre : `Pedido #${order.id_pedido}`,
                    subtitle: product ? (product.categoria || 'Producto') : 'General',
                    details: `Items: ${order.items ? order.items.length : 0} - Fecha: ${new Date(order.fecha_creacion).toLocaleDateString()}`,
                    price: `$${order.total}`,
                    total: `$${order.total}`,
                    image: product ? (product.imagen || product.image) : 'https://placehold.co/112x95/E5E7EB/666666?text=No+Image',
                    // Guardar datos completos para el modal
                    fullData: order
                }
            })

            setAllOrders(mappedOrders)
            // applyFilters se ejecutará automáticamente por el useEffect
        } catch (error) {
            console.error('Error loading orders:', error)
            setError('No se pudieron cargar las órdenes')
            setOrders([])
        } finally {
            setLoading(false)
        }
    }

    const handleVerDetalles = async (order) => {
        console.log('Abriendo detalles del pedido:', order)
        setSelectedOrderDetails(order)
        setLoadingDetail(true)
        setShowDetailsModal(true)

        try {
            // Llamar al endpoint de detalle del pedido
            const response = await fetch(`http://127.0.0.1:8003/api/pedidos/${order.id}/detalle`)
            if (response.ok) {
                const detailData = await response.json()
                setOrderDetailData(detailData)
                console.log('Datos del detalle del pedido:', detailData)
            } else {
                console.error('Error al obtener detalle del pedido:', response.status)
                setOrderDetailData(null)
            }
        } catch (error) {
            console.error('Error al cargar detalle del pedido:', error)
            setOrderDetailData(null)
        } finally {
            setLoadingDetail(false)
        }
    }

    const handleCloseDetailsModal = () => {
        setShowDetailsModal(false)
        setSelectedOrderDetails(null)
        setOrderDetailData(null)
        setLoadingDetail(false)
    }

    if (loading) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-600 dark:text-zinc-400">Cargando órdenes...</p>
            </div>
        )
    }

    if (error && orders.length === 0) {
        return (
            <div className="text-center py-12">
                <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
        )
    }

    return (
        <>
            <div className="space-y-6">
                {orders.map((order) => (
                    <div
                        key={order.id}
                        className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden"
                    >
                        {/* Header con estado */}
                        <div className="bg-gray-50 dark:bg-zinc-800 px-6 py-4 border-b border-gray-100 dark:border-zinc-700">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className={`w-3 h-3 rounded-full ${
                                        order.statusKey === 'pending' ? 'bg-yellow-400' :
                                        order.statusKey === 'shipped' ? 'bg-green-400' :
                                        'bg-blue-400'
                                    }`}></div>
                                    <span className="text-lg font-semibold text-gray-900 dark:text-zinc-100">
                                        Pedido #{order.id}
                                    </span>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                    order.statusKey === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                    order.statusKey === 'shipped' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                    'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                }`}>
                                    {order.status}
                                </span>
                            </div>
                        </div>

                        {/* Contenido principal */}
                        <div className="p-6">
                            <div className="flex flex-col lg:flex-row gap-6">
                                {/* Imagen del producto */}
                                <div className="flex-shrink-0">
                                    <div className="w-24 h-24 bg-gray-100 dark:bg-zinc-800 rounded-lg overflow-hidden mx-auto lg:mx-0">
                                        <img
                                            src={order.image}
                                            alt={order.title}
                                            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                                        />
                                    </div>
                                </div>

                                {/* Información del pedido */}
                                <div className="flex-1 space-y-4">
                                    <div>
                                        <h4 className="text-lg font-medium text-gray-900 dark:text-zinc-100 mb-2">
                                            {order.title}
                                        </h4>
                                        <p className="text-sm text-gray-600 dark:text-zinc-400">
                                            {order.subtitle}
                                        </p>
                                    </div>

                                    {/* Detalles con íconos */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-zinc-400">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                                            </svg>
                                            {order.details.split(' - ')[0]}
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-zinc-400">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                            </svg>
                                            {order.details.split(' - ')[1]}
                                        </div>
                                    </div>
                                </div>

                                {/* Precio y acciones */}
                                <div className="flex flex-col items-end justify-between gap-4">
                                    <div className="text-right">
                                        <p className="text-2xl font-bold text-gray-900 dark:text-zinc-100">
                                            ${order.total}
                                        </p>
                                        <p className="text-sm text-gray-500 dark:text-zinc-500">
                                            Total pagado
                                        </p>
                                    </div>

                                    <div className="flex flex-col gap-2 w-full lg:w-auto">
                                        {order.statusKey === 'pending' && (
                                            <button className="w-full lg:w-32 px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                                </svg>
                                                Pagar ahora
                                            </button>
                                        )}

                                        {order.statusKey === 'shipped' && (
                                            <button className="w-full lg:w-32 px-4 py-2 bg-green-500 hover:bg-green-600 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.1 5H19M7 13v8a2 2 0 002 2h10a2 2 0 002-2v-3" />
                                                </svg>
                                                Añadir al carrito
                                            </button>
                                        )}

                                        <button
                                            onClick={() => {
                                                console.log('Botón Ver detalles clickeado', order)
                                                handleVerDetalles(order)
                                            }}
                                            className="w-full lg:w-32 px-4 py-2 border border-gray-300 dark:border-zinc-600 text-gray-700 dark:text-zinc-300 hover:bg-gray-50 dark:hover:bg-zinc-800 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                            Ver detalles
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Modal de Detalles */}
            {showDetailsModal && selectedOrderDetails && (
                <Modal isOpen={showDetailsModal} onClose={handleCloseDetailsModal}>
                    <div className="p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-100 mb-4">
                            Detalles del Pedido #{selectedOrderDetails.id}
                        </h2>

                        <div className="space-y-4">
                            {/* Información del Cliente */}
                            {loadingDetail ? (
                                <div className="text-center py-4">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                                    <p className="text-sm text-gray-500 mt-2">Cargando detalles...</p>
                                </div>
                            ) : orderDetailData ? (
                                <>
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-2">
                                            Información del Cliente
                                        </h3>
                                        <div className="bg-gray-50 dark:bg-zinc-800 p-4 rounded-lg">
                                            <div className="flex items-start gap-3">
                                                <svg className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                                </svg>
                                                <div className="text-sm text-gray-600 dark:text-zinc-400">
                                                    <p><strong>Nombre:</strong> {orderDetailData.cliente.nombre} {orderDetailData.cliente.apellido}</p>
                                                    <p><strong>Email:</strong> {orderDetailData.cliente.correo}</p>
                                                    <p><strong>Teléfono:</strong> {orderDetailData.cliente.telefono}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-2">
                                            Dirección de Envío
                                        </h3>
                                        <div className="bg-gray-50 dark:bg-zinc-800 p-4 rounded-lg">
                                            <div className="flex items-start gap-3">
                                                <svg className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                </svg>
                                                <div className="text-sm text-gray-600 dark:text-zinc-400">
                                                    <p><strong>Calle:</strong> {orderDetailData.direccion.calle}</p>
                                                    <p><strong>Ciudad:</strong> {orderDetailData.direccion.ciudad}</p>
                                                    <p><strong>Estado:</strong> {orderDetailData.direccion.estado}</p>
                                                    <p><strong>Código Postal:</strong> {orderDetailData.direccion.codigo_postal}</p>
                                                    {orderDetailData.direccion.referencias && (
                                                        <p><strong>Referencias:</strong> {orderDetailData.direccion.referencias}</p>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="text-center py-4">
                                    <p className="text-sm text-red-500">Error al cargar los detalles del pedido</p>
                                </div>
                            )}

                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-2">
                                    Información del Pedido
                                </h3>
                                <div className="bg-gray-50 dark:bg-zinc-800 p-4 rounded-lg space-y-2">
                                    <p><strong>ID del Pedido:</strong> {orderDetailData ? orderDetailData.id_pedido : selectedOrderDetails.id}</p>
                                    <p><strong>Estado:</strong> {orderDetailData ? orderDetailData.estado : selectedOrderDetails.status}</p>
                                    <p><strong>Fecha:</strong> {orderDetailData ? new Date(orderDetailData.fecha_creacion).toLocaleDateString() : (selectedOrderDetails.fullData?.fecha_creacion ? new Date(selectedOrderDetails.fullData.fecha_creacion).toLocaleDateString() : 'Fecha no disponible')}</p>
                                    <p><strong>Total:</strong> ${orderDetailData ? orderDetailData.total : selectedOrderDetails.total}</p>
                                    <p><strong>Items:</strong> {selectedOrderDetails.fullData?.items ? selectedOrderDetails.fullData.items.length : 0}</p>
                                </div>
                            </div>

                            {selectedOrderDetails.fullData?.items && selectedOrderDetails.fullData.items.length > 0 && (
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-2">
                                        Productos
                                    </h3>
                                    <div className="bg-gray-50 dark:bg-zinc-800 p-4 rounded-lg">
                                        {selectedOrderDetails.fullData.items.map((item, index) => (
                                            <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-zinc-700 last:border-b-0">
                                                <div>
                                                    <p className="font-medium">{item.producto?.nombre || 'Producto'}</p>
                                                    <p className="text-sm text-gray-600 dark:text-zinc-400">
                                                        Cantidad: {item.cantidad} × ${item.precio_unitario}
                                                    </p>
                                                </div>
                                                <p className="font-semibold">${(item.cantidad * item.precio_unitario).toFixed(2)}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="flex justify-end mt-6">
                            <button
                                onClick={handleCloseDetailsModal}
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </Modal>
            )}
        </>
    )
}