import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { ProductImage } from "../components/product-detail/ProductImage"
import { ProductInfo } from "../components/product-detail/ProductInfo"
import { ProductoService } from "../services/apiservice"

export function ProductDetail() {
    const { id } = useParams()
    const [product, setProduct] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    
    // Estado inicial null para que no haya selección por defecto
    const [selectedColor, setSelectedColor] = useState(null)
    const [selectedSize, setSelectedSize] = useState(null)

    // Desactivar scroll al montar el componente
    useEffect(() => {
        document.body.style.overflow = "hidden"
        return () => {
            document.body.style.overflow = "unset"
        }
    }, [])

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                setLoading(true)
                const data = await ProductoService.obtenerPorId(id)
                
                // Adaptar datos del backend al formato esperado por el componente
                // El backend devuelve: { id, nombre, precio, imagen, categoria, ... }
                // Necesitamos simular colores y tallas si no vienen del backend
                
                const adaptedProduct = {
                    id: data.id,
                    name: data.nombre || data.name,
                    price: typeof data.precio === 'number' ? `$${data.precio.toFixed(2)}` : data.precio,
                    description: data.descripcion,
                    // Usar imagen del producto o placeholder
                    image: data.imagen || data.image || "https://placehold.co/800x1000/E5E7EB/333333?text=No+Image",
                    // Simular variantes si no existen
                    colors: [
                        {
                            id: "default",
                            name: "Único",
                            image: data.imagen || data.image || "https://placehold.co/800x1000/E5E7EB/333333?text=No+Image",
                            thumbnail: data.imagen || data.image || "https://placehold.co/100x120/E5E7EB/333333?text=Unique"
                        }
                    ],
                    sizes: [
                        { name: "XCH", inStock: true },
                        { name: "CH", inStock: true },
                        { name: "M", inStock: true },
                        { name: "XG", inStock: true },
                        { name: "XXG", inStock: false }
                    ]
                }
                
                setProduct(adaptedProduct)
                // Seleccionar color por defecto
                setSelectedColor("default")
            } catch (err) {
                console.error("Error loading product:", err)
                setError("No se pudo cargar el producto")
            } finally {
                setLoading(false)
            }
        }

        if (id) {
            fetchProduct()
        }
    }, [id])

    if (loading) {
        return (
            <div className="h-[calc(100vh-73px)] flex items-center justify-center bg-white dark:bg-zinc-900">
                <p className="text-gray-600 dark:text-zinc-400">Cargando producto...</p>
            </div>
        )
    }

    if (error || !product) {
        return (
            <div className="h-[calc(100vh-73px)] flex items-center justify-center bg-white dark:bg-zinc-900">
                <p className="text-red-600 dark:text-red-400">{error || "Producto no encontrado"}</p>
            </div>
        )
    }

    // Si hay color seleccionado, usamos sus datos. Si no, usamos el primero por defecto para la imagen principal (pero sin seleccionarlo)
    const currentColorData = selectedColor
        ? product.colors.find(c => c.id === selectedColor)
        : product.colors[0]

    return (
        <div className="h-[calc(100vh-73px)] bg-white dark:bg-zinc-900 transition-colors duration-300 overflow-hidden">
            <div className="flex flex-col lg:flex-row h-full">

                <ProductImage
                    image={currentColorData?.image}
                    name={product.name}
                />

                <ProductInfo
                    product={product}
                    selectedColor={selectedColor}
                    setSelectedColor={setSelectedColor}
                    selectedSize={selectedSize}
                    setSelectedSize={setSelectedSize}
                    currentColorData={selectedColor ? currentColorData : null} // Pasamos null si no hay selección para que el label diga "Selecciona un color"
                />

            </div>
        </div>
    )
}
