import { useNavigate } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'

export function AccountSidebar({ activeSection, onSectionChange, isOpen = false, onClose = () => { } }) {
    const navigate = useNavigate()
    const [indicatorStyle, setIndicatorStyle] = useState({ top: 0, height: 0 })
    const itemsRef = useRef({})

    const sections = [
        { id: 'general', label: 'General' },
        { id: 'pedidos', label: 'Pedidos' },
        { id: 'metodos-pago', label: 'Métodos de pago' },
        { id: 'reembolso', label: 'Reembolso' },
        { id: 'feedback', label: 'Feedback' },
        { id: 'configuracion', label: 'Configuración' },
        { id: 'domicilios', label: 'Domicilios de envío' },
        { id: 'centro-mensajes', label: 'Centro de mensajes' },
        { id: 'atencion', label: 'Atención al cliente' }
    ]

    useEffect(() => {
        const activeItem = itemsRef.current[activeSection]
        if (activeItem) {
            setIndicatorStyle({
                top: activeItem.offsetTop,
                height: activeItem.offsetHeight
            })
        }
    }, [activeSection])

    return (
        <>
            {/* Mobile Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity duration-300 ease-in-out"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <div className={`
                fixed lg:static top-0 left-0 h-full lg:h-auto
                w-[280px] sm:w-[325px] lg:w-[325px]
                flex flex-col gap-6 flex-shrink-0
                lg:sticky lg:top-6 self-start
                bg-[rgb(245,245,245)] dark:bg-zinc-950 lg:bg-transparent
                z-50 lg:z-auto
                transform transition-all duration-500 ease-[cubic-bezier(.15,.83,.66,1)]
                ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
                overflow-y-auto lg:overflow-visible
                pt-4 lg:pt-0
            `}>
                {/* Mobile Close Button */}
                <button
                    onClick={onClose}
                    className="lg:hidden absolute top-4 right-4 text-black dark:text-zinc-100 p-2 hover:scale-110 transition-transform duration-300 rounded-full hover:bg-black/10 dark:hover:bg-white/10"
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                </button>

                {/* Account Navigation Container */}
                <div className="bg-white dark:bg-zinc-900 mx-4 lg:mx-0">
                    {/* Header */}
                    <div className="px-5 pt-6 pb-4">
                        <h2 className="text-base font-normal text-black dark:text-zinc-100 hover:scale-105 transition-transform duration-300 cursor-default">
                            Cuenta
                        </h2>
                    </div>

                    {/* Navigation */}
                    <nav className="relative">
                        {/* Sliding Indicator */}
                        <div
                            className="absolute left-0 w-1 bg-[rgb(169,191,162)] z-10 transition-all duration-500 ease-[cubic-bezier(.15,.83,.66,1)] shadow-lg"
                            style={{
                                top: `${indicatorStyle.top}px`,
                                height: `${indicatorStyle.height}px`
                            }}
                        />

                        {sections.map((section) => (
                            <div
                                key={section.id}
                                ref={el => itemsRef.current[section.id] = el}
                                className="relative h-[35px]"
                            >
                                <button
                                    onClick={() => onSectionChange(section.id)}
                                    className={`w-full h-full text-left px-5 text-base font-light transition-all duration-300 hover:scale-105 hover:translate-x-2 ${activeSection === section.id
                                        ? 'bg-[rgb(245,245,245)] dark:bg-zinc-800 text-[rgb(77,76,76)] dark:text-zinc-300'
                                        : 'text-[rgb(77,76,76)] dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-800 hover:text-[rgb(77,76,76)] dark:hover:text-zinc-300'
                                        }`}
                                >
                                    {section.label}
                                </button>
                            </div>
                        ))}
                    </nav>
                </div>

                {/* QR Code Container - Hidden on mobile */}
                <div className="hidden lg:block bg-white dark:bg-zinc-900 px-5 py-6 mx-4 lg:mx-0 hover:scale-105 transition-transform duration-500 ease-out hover:shadow-lg">
                    <p className="text-base font-light text-black dark:text-zinc-100 text-center mb-2">
                        Vandentials Mobile App
                    </p>
                    <p className="text-base font-light text-[rgb(77,76,76)] dark:text-zinc-400 text-center mb-4">
                        Escanea ahora para obtener la app
                    </p>
                    <div className="flex justify-center">
                        <img
                            src="https://placehold.co/185x185/E5E7EB/9CA3AF?text=QR+Code"
                            alt="QR Code"
                            className="w-[185px] h-[185px]"
                        />
                    </div>
                </div>
            </div>
        </>
    )
}
