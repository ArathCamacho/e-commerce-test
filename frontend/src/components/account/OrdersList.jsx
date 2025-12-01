import { useState, useEffect } from 'react'
import orderService from '../../services/orderService'

export function OrdersList() {
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadOrders()
    }, [])

    const loadOrders = async () => {
        try {
            setLoading(true)
            const response = await orderService.getOrders()
            setOrders(response.data)
        } catch (error) {
            console.error('Error loading orders:', error)
            setError('No se pudieron cargar las órdenes')
            // Fallback a datos de ejemplo
            setOrders([
                {
                    id: 1,
                    status: 'Por pagar',
                    statusKey: 'pending',
                    title: 'Zuecos',
                    subtitle: 'Zuecos/Unisex',
                    details: 'Talla 43, Color Verde Olivo',
                    price: 'MX $2300',
                    total: 'MX $2300 + Envío',
                    image: 'https://via.placeholder.com/112x95/E5E7EB/666666?text=Zuecos'
                },
                {
                    id: 2,
                    status: 'Enviado',
                    statusKey: 'shipped',
                    title: 'Camisa de verano',
                    subtitle: 'Camisa de verano/Hombre',
                    details: 'Talla M, Color caqui',
                    price: 'MX $450',
                    total: 'MX $450 + Envío',
                    image: 'https://via.placeholder.com/112x95/E5E7EB/666666?text=Camisa'
                },
                {
                    id: 3,
                    status: 'Enviado',
                    statusKey: 'shipped',
                    title: 'Bermudas',
                    subtitle: 'Bermudas/Hombre',
                    details: 'Talla 28x30, Color café oscuro',
                    price: 'MX $700',
                    total: 'MX $700 + Envío',
                    image: 'https://via.placeholder.com/112x95/E5E7EB/666666?text=Bermudas'
                }
            ])
        } finally {
            setLoading(false)
        }
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
        <div className="space-y-6">
            {orders.map((order) => (
                <div
                    key={order.id}
                    className="bg-white dark:bg-zinc-900 w-full"
                    style={{
                        minHeight: '200px',
                        padding: '14px 16px'
                    }}
                >
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 sm:mb-5 gap-2 sm:gap-0">
                        <h3 className="text-sm sm:text-base font-normal text-black dark:text-zinc-100">
                            {order.status}
                        </h3>
                        <button className="text-sm sm:text-base font-light text-black dark:text-zinc-100 hover:underline flex items-center gap-2">
                            Detalles del pedido
                            <svg width="8" height="16" viewBox="0 0 8 16" fill="none">
                                <path d="M1 1L7 8L1 15" stroke="currentColor" strokeWidth="1.5" />
                            </svg>
                        </button>
                    </div>

                    {/* Divider */}
                    <div className="w-full h-px bg-gray-300 dark:bg-zinc-700 mb-4" />

                    {/* Order Content */}
                    <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
                        {/* Product Image */}
                        <div
                            className="flex-shrink-0 bg-gray-100 dark:bg-zinc-800 mx-auto sm:mx-0"
                            style={{ width: '112px', height: '95px' }}
                        >
                            <img
                                src={order.image}
                                alt={order.title}
                                className="w-full h-full object-cover"
                            />
                        </div>

                        {/* Product Info */}
                        <div className="flex-1 text-center sm:text-left">
                            <h4 className="text-sm sm:text-base font-light text-[rgb(77,76,76)] dark:text-zinc-300 mb-2">
                                {order.subtitle}
                            </h4>
                            <p className="text-sm sm:text-base font-light text-[rgb(147,146,146)] dark:text-zinc-500 mb-2">
                                {order.details}
                            </p>
                            <p className="text-sm sm:text-base font-normal text-black dark:text-zinc-100">
                                {order.price}
                            </p>
                        </div>

                        {/* Price and Actions */}
                        <div className="flex flex-col items-center sm:items-end justify-between gap-3 sm:gap-0 w-full sm:w-auto" style={{ minWidth: 'auto', maxWidth: '100%' }}>
                            <p className="text-sm sm:text-base font-normal text-black dark:text-zinc-100 text-center w-full sm:w-[168px]">
                                {order.total}
                            </p>

                            <div className="flex flex-col gap-3 w-full sm:w-auto items-stretch sm:items-end">
                                {order.statusKey === 'pending' && (
                                    <button
                                        className="w-full sm:w-[168px] h-[32px] sm:h-[26px] bg-[rgb(169,191,162)] text-white text-sm sm:text-base font-medium hover:bg-[rgb(159,181,152)] transition-colors"
                                    >
                                        Pagar ahora
                                    </button>
                                )}

                                {order.statusKey === 'shipped' && (
                                    <button
                                        className="w-full sm:w-[168px] h-[32px] sm:h-[26px] bg-[rgb(169,191,162)] text-white text-sm sm:text-base font-medium hover:bg-[rgb(159,181,152)] transition-colors"
                                    >
                                        Añadir al carrito
                                    </button>
                                )}

                                <button
                                    className="w-full sm:w-[168px] h-[32px] sm:h-[26px] border border-black dark:border-zinc-400 text-black dark:text-zinc-100 text-sm sm:text-base font-medium hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors"
                                >
                                    Modificar dirección
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
