import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AccountSidebar } from '../components/account/AccountSidebar'
import { OrdersList } from '../components/account/OrdersList'
import { ShippingAddresses } from '../components/account/ShippingAddresses'
import { PaymentMethods } from '../components/account/PaymentMethods'
import { GeneralProfile } from '../components/account/GeneralProfile'

export function Account() {
    const navigate = useNavigate()
    const [activeSection, setActiveSection] = useState('general')
    const [filterStatus, setFilterStatus] = useState('all')
    const [timeFilter, setTimeFilter] = useState('last-year')
    const [underlineStyle, setUnderlineStyle] = useState({ left: 0, width: 0 })
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const tabsRef = useRef({})
    const tabsContainerRef = useRef(null)

    useEffect(() => {
        const activeTab = tabsRef.current[filterStatus]
        const container = tabsContainerRef.current

        if (activeTab && container) {
            // Get the parent container's padding
            const containerRect = container.getBoundingClientRect()
            const tabRect = activeTab.getBoundingClientRect()

            // Calculate position relative to the main container (including padding)
            const leftOffset = tabRect.left - containerRect.left

            setUnderlineStyle({
                left: leftOffset,
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
            <div className="bg-[rgb(245,245,245)] dark:bg-zinc-950 px-4 sm:px-6 lg:px-[53px] pt-6 pb-4">
                <div className="flex items-center gap-2 text-sm sm:text-base overflow-x-auto">
                    <button
                        onClick={() => navigate('/')}
                        className="text-[rgb(77,76,76)] dark:text-zinc-400 font-light hover:underline whitespace-nowrap"
                    >
                        Home
                    </button>
                    <svg width="6" height="12" viewBox="0 0 6 12" fill="none" className="text-[rgb(77,76,76)] dark:text-zinc-400 flex-shrink-0">
                        <path d="M1 1L5 6L1 11" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                    <button
                        onClick={() => setActiveSection('general')}
                        className="text-[rgb(77,76,76)] dark:text-zinc-400 font-light hover:underline whitespace-nowrap"
                    >
                        Cuenta
                    </button>
                    <svg width="6" height="12" viewBox="0 0 6 12" fill="none" className="text-[rgb(77,76,76)] dark:text-zinc-400 flex-shrink-0">
                        <path d="M1 1L5 6L1 11" stroke="currentColor" strokeWidth="1.5" />
                    </svg>
                    <span className="text-[rgb(77,76,76)] dark:text-zinc-300 font-semibold whitespace-nowrap">
                        {getSectionLabel()}
                    </span>
                </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-0 lg:gap-8 px-4 sm:px-6 lg:px-[53px] items-start">
                {/* Mobile Menu Button */}
                <button
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="lg:hidden mb-4 flex items-center gap-2 text-base font-normal text-black dark:text-zinc-100 bg-white dark:bg-zinc-900 px-4 py-3 w-full"
                >
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" className="text-black dark:text-zinc-100">
                        <path d="M2 5h16M2 10h16M2 15h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                    <span>Menú de cuenta</span>
                    <span className="ml-auto text-sm text-[rgb(77,76,76)] dark:text-zinc-400">{getSectionLabel()}</span>
                </button>

                {/* Sidebar */}
                <AccountSidebar
                    activeSection={activeSection}
                    onSectionChange={(section) => {
                        setActiveSection(section)
                        setSidebarOpen(false)
                    }}
                    isOpen={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                />

                {/* Main Content */}
                <div className="flex-1 w-full lg:w-auto pt-0 lg:pt-6 pb-12">
                    {activeSection === 'pedidos' && (
                        <>
                            {/* Filters Bar */}
                            <div
                                ref={tabsContainerRef}
                                className="bg-white dark:bg-zinc-900 mb-6 relative w-full"
                            >
                                {/* Content wrapper with padding */}
                                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between px-3 sm:px-5 py-3 sm:py-0 gap-3 sm:gap-0" style={{ minHeight: '47px' }}>
                                    {/* Tabs container */}
                                    <div className="flex gap-4 sm:gap-8 relative overflow-x-auto scrollbar-hide" style={{ height: '47px' }}>
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
                                                    className={`text-sm sm:text-base transition-colors relative h-full flex items-center whitespace-nowrap px-1 ${filterStatus === status
                                                        ? 'text-black dark:text-zinc-100 font-normal'
                                                        : 'text-[rgb(77,76,76)] dark:text-zinc-400 font-light'
                                                        }`}
                                                >
                                                    {labels[status]}
                                                </button>
                                            )
                                        })}
                                    </div>

                                    {/* Time Filter */}
                                    <select
                                        value={timeFilter}
                                        onChange={(e) => setTimeFilter(e.target.value)}
                                        className="w-full sm:w-[215px] h-[35px] sm:h-[25px] px-3 border border-[rgb(77,76,76)] dark:border-zinc-700 text-sm sm:text-base font-light text-black dark:text-zinc-100 bg-white dark:bg-zinc-900 focus:outline-none"
                                    >
                                        <option value="last-year">Todo/Último año</option>
                                        <option value="last-month">Último mes</option>
                                        <option value="last-week">Última semana</option>
                                    </select>
                                </div>

                                {/* Sliding Underline - positioned at absolute bottom of container */}
                                <div
                                    className="absolute bottom-0 left-0 right-0 h-1 bg-transparent hidden sm:block"
                                >
                                    <div
                                        className="h-full bg-[rgb(169,191,162)] transition-all duration-300 ease-in-out"
                                        style={{
                                            marginLeft: `${underlineStyle.left}px`,
                                            width: `${underlineStyle.width}px`
                                        }}
                                    />
                                </div>

                            </div>

                            {/* Orders List */}
                            <OrdersList />
                        </>
                    )}

                    {activeSection === 'domicilios' && <ShippingAddresses />}

                    {activeSection === 'metodos-pago' && <PaymentMethods />}

                    {activeSection === 'general' && <GeneralProfile />}

                    {activeSection !== 'pedidos' && activeSection !== 'domicilios' && activeSection !== 'metodos-pago' && activeSection !== 'general' && (
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
