import { useNavigate } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'

export function AccountSidebar({ activeSection, onSectionChange }) {
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
        <div className="w-[325px] flex flex-col gap-6 flex-shrink-0 sticky top-6 self-start">
            {/* Account Navigation Container */}
            <div className="bg-white dark:bg-zinc-900">
                {/* Header */}
                <div className="px-5 pt-6 pb-4">
                    <h2 className="text-base font-normal text-black dark:text-zinc-100">
                        Cuenta
                    </h2>
                </div>

                {/* Navigation */}
                <nav className="relative">
                    {/* Sliding Indicator */}
                    <div
                        className="absolute left-0 w-1 bg-[rgb(169,191,162)] z-10 transition-all duration-300 ease-in-out"
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
                                className={`w-full h-full text-left px-5 text-base font-light transition-colors ${activeSection === section.id
                                    ? 'bg-[rgb(245,245,245)] dark:bg-zinc-800 text-[rgb(77,76,76)] dark:text-zinc-300'
                                    : 'text-[rgb(77,76,76)] dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-800'
                                    }`}
                            >
                                {section.label}
                            </button>
                        </div>
                    ))}
                </nav>
            </div>

            {/* QR Code Container */}
            <div className="bg-white dark:bg-zinc-900 px-5 py-6">
                <p className="text-base font-light text-black dark:text-zinc-100 text-center mb-2">
                    Vandentials Mobile App
                </p>
                <p className="text-base font-light text-[rgb(77,76,76)] dark:text-zinc-400 text-center mb-4">
                    Escanea ahora para obtener la app
                </p>
                <div className="flex justify-center">
                    <img
                        src="https://via.placeholder.com/185x185/E5E7EB/9CA3AF?text=QR+Code"
                        alt="QR Code"
                        className="w-[185px] h-[185px]"
                    />
                </div>
            </div>
        </div>
    )
}
