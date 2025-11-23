import { useState, useEffect } from "react"
import { ProductImage } from "../components/product-detail/ProductImage"
import { ProductInfo } from "../components/product-detail/ProductInfo"

export function ProductDetail() {
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

    const product = {
        name: "PLAYERA POLO SLIM FIT TEXTURIZADA",
        price: "$499.00",
        colors: [
            {
                id: "verde-olivo",
                name: "Verde Olivo",
                image: "https://via.placeholder.com/800x1000/9CA986/FFFFFF?text=Verde+Olivo",
                thumbnail: "https://via.placeholder.com/100x120/9CA986/FFFFFF?text=V"
            },
            {
                id: "beige",
                name: "Beige",
                image: "https://via.placeholder.com/800x1000/C8B896/FFFFFF?text=Beige",
                thumbnail: "https://via.placeholder.com/100x120/C8B896/FFFFFF?text=B"
            },
            {
                id: "gris",
                name: "Gris",
                image: "https://via.placeholder.com/800x1000/6B7280/FFFFFF?text=Gris",
                thumbnail: "https://via.placeholder.com/100x120/6B7280/FFFFFF?text=G"
            },
            {
                id: "blanco",
                name: "Blanco",
                image: "https://via.placeholder.com/800x1000/F3F4F6/333333?text=Blanco",
                thumbnail: "https://via.placeholder.com/100x120/F3F4F6/333333?text=B"
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
