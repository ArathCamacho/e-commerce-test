import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AccountSidebar } from '../components/account/AccountSidebar'
import { OrdersList } from '../components/account/OrdersList'
import { ShippingAddresses } from '../components/account/ShippingAddresses'
import { PaymentMethods } from '../components/account/PaymentMethods'

export function Account() {
    const navigate = useNavigate()
    const [activeSection, setActiveSection] = useState('general')
    const [filterStatus, setFilterStatus] = useState('all')
    const [timeFilter, setTimeFilter] = useState('last-year')
    const [underlineStyle, setUnderlineStyle] = useState({ left: 0, width: 0 })
    const tabsRef = useRef({})

    useEffect(() => {
        const activeTab = tabsRef.current[filterStatus]
        if (activeTab) {
            setUnderlineStyle({
                left: activeTab.offsetLeft,
                width: activeTab.offsetWidth
            })
        }
    }, [filterStatus, activeSection])

    const getSectionLabel = () => {
        const labels = {
            'general': 'General',
            'pedidos': 'Pedidos',
            'metodos-pago': 'Métodos de pago',
            'reembolso': 'Reembolso',
            'feedback': 'Feedback',
            'configuracion': 'Configuración',
            'domicilios': 'Domicilios de envío',
            'centro-mensajes': 'Centro de mensajes',
            'atencion': 'Atención al cliente'
        }
        return labels[activeSection] || 'General'
    }

    return (
        <div className="min-h-screen bg-[rgb(245,245,245)] dark:bg-zinc-950 transition-colors duration-300 font-['Lato']">
            {/* Breadcrumb */}
            <div className="bg-[rgb(245,245,245)] dark:bg-zinc-950 px-[53px] pt-6 pb-4">
                <div className="flex items-center gap-2 text-base">
                    <button
                        onClick={() => navigate('/')}
                        className="text-[rgb(77,76,76)] dark:text-zinc-400 font-light hover:underline"
                    >
                        Home
                    </button>
                    <svg width="6" height="12" viewBox="0 0 6 12" fill="none" className="text-[rgb(77,76,76)] dark:text-zinc-400">
                        <path d="M1 1L5 6L1 11" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                    <button
                        onClick={() => setActiveSection('general')}
                        className="text-[rgb(77,76,76)] dark:text-zinc-400 font-light hover:underline"
                    >
                        Cuenta
                    </button>
                    <svg width="6" height="12" viewBox="0 0 6 12" fill="none" className="text-[rgb(77,76,76)] dark:text-zinc-400">
                        <path d="M1 1L5 6L1 11" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                    <span className="text-[rgb(77,76,76)] dark:text-zinc-300 font-semibold">
                        {getSectionLabel()}
                    </span>
                </div>
            </div>

            <div className="flex gap-8 px-[53px] items-start">
                {/* Sidebar */}
                <AccountSidebar
                    activeSection={activeSection}
                    onSectionChange={setActiveSection}
                />

                {/* Main Content */}
                <div className="flex-1 pt-6 pb-12">
                    {activeSection === 'pedidos' && (
                        <>
                            {/* Filters Bar */}
                            <div
                                className="bg-white dark:bg-zinc-900 flex items-center justify-between px-5 mb-6 relative overflow-hidden w-full"
                                style={{ height: '47px' }}
                            >
                                <div className="flex gap-8 h-full relative">
                                    {['all', 'pending', 'shipping', 'shipped', 'processed'].map((status) => {
                                        const labels = {
                                            all: 'Ver todo',
                                            pending: 'Por pagar',
                                            shipping: 'Por enviar',
                                            shipped: 'Enviado',
                                            processed: 'Procesado'
                                        }
                                        return (
                                            <button
                                                key={status}
                                                ref={el => tabsRef.current[status] = el}
                                                onClick={() => setFilterStatus(status)}
                                                className={`text-base transition-colors relative h-full flex items-center ${filterStatus === status
                                                    ? 'text-black dark:text-zinc-100 font-normal'
                                                    : 'text-[rgb(77,76,76)] dark:text-zinc-400 font-light'
                                                    }`}
                                            >
                                                {labels[status]}
                                            </button>
                                        )
                                    })}
                                    {/* Sliding Underline */}
                                    <div
                                        className="absolute bottom-0 h-1 bg-[rgb(169,191,162)] transition-all duration-300 ease-in-out"
                                        style={{
                                            left: `${underlineStyle.left}px`,
                                            width: `${underlineStyle.width}px`
                                        }}
                                    />
                                </div>

                                {/* Time Filter */}
                                <select
                                    value={timeFilter}
                                    onChange={(e) => setTimeFilter(e.target.value)}
                                    className="w-[215px] h-[25px] px-3 border border-[rgb(77,76,76)] dark:border-zinc-700 text-base font-light text-black dark:text-zinc-100 bg-white dark:bg-zinc-900 focus:outline-none"
                                >
                                    <option value="last-year">Todo/Último año</option>
                                    <option value="last-month">Último mes</option>
                                    <option value="last-week">Última semana</option>
                                </select>
                            </div>

                            {/* Orders List */}
                            <OrdersList />
                        </>
                    )}

                    {activeSection === 'domicilios' && <ShippingAddresses />}

                    {activeSection === 'metodos-pago' && <PaymentMethods />}

                    {activeSection !== 'pedidos' && activeSection !== 'domicilios' && activeSection !== 'metodos-pago' && (
                        <div className="bg-white dark:bg-zinc-900 p-12 text-center w-full">
                            <p className="text-[rgb(77,76,76)] dark:text-zinc-400 text-base font-light">
                                Sección "{getSectionLabel()}" en construcción
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
