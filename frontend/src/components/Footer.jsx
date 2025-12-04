import { Facebook, Instagram, Twitter, Mail, Phone, MapPin } from "lucide-react"

export function Footer() {
    return (
        <footer className="bg-zinc-800  dark:bg-zinc-950 text-gray-300 dark:text-zinc-400 transition-colors duration-300">
            {/* Main Footer Content */}
            <div className="max-w-7xl mx-auto px-4 py-12 md:py-16">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
                    {/* About Section */}
                    <div>
                        <div className="flex items-center gap-2 mb-6">
                            <div className="w-10 h-10 bg-[#A9BFA2] rounded-full flex items-center justify-center">
                                <span className="text-white font-bold text-lg">V</span>
                            </div>
                            <span className="text-lg font-bold text-white tracking-wide">
                                <span className="text-[#A9BFA2]">VAND</span>ENTIALS
                            </span>
                        </div>
                        <p className="text-sm text-gray-400 dark:text-zinc-500 leading-relaxed">
                            Tu destino para moda de calidad. Descubre las últimas tendencias y estilos que definen tu personalidad.
                        </p>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Enlaces Rápidos</h3>
                        <ul className="space-y-3">
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Sobre Nosotros
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Catálogo
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Ofertas
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Blog
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Customer Service */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Atención al Cliente</h3>
                        <ul className="space-y-3">
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Envíos y Devoluciones
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Preguntas Frecuentes
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Términos y Condiciones
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    Política de Privacidad
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Contact Info */}
                    <div>
                        <h3 className="text-white font-semibold mb-4">Contacto</h3>
                        <ul className="space-y-3">
                            <li className="flex items-start gap-2">
                                <MapPin className="w-4 h-4 mt-1 flex-shrink-0 text-[#A9BFA2]" />
                                <span className="text-sm">
                                    Hermosillo, Sonora
                                    <br />
                                    México
                                </span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Phone className="w-4 h-4 flex-shrink-0 text-[#A9BFA2]" />
                                <a href="tel:+526621234567" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    +52 (662) 123-4567
                                </a>
                            </li>
                            <li className="flex items-center gap-2">
                                <Mail className="w-4 h-4 flex-shrink-0 text-[#A9BFA2]" />
                                <a href="mailto:info@vandentials.com" className="text-sm hover:text-[#A9BFA2] transition-colors">
                                    info@vandentials.com
                                </a>
                            </li>
                        </ul>

                        {/* Social Media */}
                        <div className="mt-6">
                            <h4 className="text-white font-semibold mb-3 text-sm">Síguenos</h4>
                            <div className="flex items-center gap-3">
                                <a
                                    href="#"
                                    className="group w-9 h-9 bg-zinc-800 dark:bg-zinc-950 rounded-full flex items-center justify-center hover:bg-[#A9BFA2] dark:hover:bg-[#A9BFA2] transition-colors hover:scale-110 transition-transform duration-300"
                                    aria-label="Facebook"
                                >
                                    <Facebook className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                                </a>
                                <a
                                    href="#"
                                    className="group w-9 h-9 bg-zinc-800 dark:bg-zinc-950 rounded-full flex items-center justify-center hover:bg-[#A9BFA2] dark:hover:bg-[#A9BFA2] transition-colors hover:scale-110 transition-transform duration-300"
                                    aria-label="Instagram"
                                >
                                    <Instagram className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                                </a>
                                <a
                                    href="#"
                                    className="group w-9 h-9 bg-zinc-800 dark:bg-zinc-950 rounded-full flex items-center justify-center hover:bg-[#A9BFA2] dark:hover:bg-[#A9BFA2] transition-colors hover:scale-110 transition-transform duration-300"
                                    aria-label="X (Twitter)"
                                >
                                    <Twitter className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-zinc-700 dark:border-zinc-900">
                <div className="max-w-7xl mx-auto px-4 py-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-gray-400 dark:text-zinc-500">
                            © 2025 Vandentials. Todos los derechos reservados.
                        </p>
                        <div className="flex items-center gap-6">
                            <a href="#" className="text-sm text-gray-400 dark:text-zinc-500 hover:text-[#A9BFA2] transition-colors">
                                Privacidad
                            </a>
                            <a href="#" className="text-sm text-gray-400 dark:text-zinc-500 hover:text-[#A9BFA2] transition-colors">
                                Términos
                            </a>
                            <a href="#" className="text-sm text-gray-400 dark:text-zinc-500 hover:text-[#A9BFA2] transition-colors">
                                Cookies
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    )
}
