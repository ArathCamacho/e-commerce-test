import React, { useState } from "react";

export function CategorySidebar({ title, count, categories, showGenderFilter = false }) {
    const [priceRange, setPriceRange] = useState([100, 10000]);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [selectedGenders, setSelectedGenders] = useState([]);

    const handleCategoryToggle = (category) => {
        setSelectedCategories(prev =>
            prev.includes(category)
                ? prev.filter(c => c !== category)
                : [...prev, category]
        );
    };

    const handleGenderToggle = (gender) => {
        setSelectedGenders(prev =>
            prev.includes(gender)
                ? prev.filter(g => g !== gender)
                : [...prev, gender]
        );
    };

    const formatPrice = (value) => {
        return `$${value.toLocaleString()}`;
    };

    return (
        <aside className="w-64 hidden lg:block flex-shrink-0">
            <div className="sticky top-24">
                <h2 className="font-bold text-2xl mb-6 text-gray-900 dark:text-zinc-100">
                    {title} ({count})
                </h2>

                {/* Gender Filter (for Kids) */}
                {showGenderFilter && (
                    <div className="mb-8">
                        <h3 className="font-semibold mb-3 text-gray-900 dark:text-zinc-200">
                            Género (2)
                        </h3>
                        <div className="space-y-2">
                            <label className="flex items-center text-sm gap-2 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={selectedGenders.includes('boys')}
                                    onChange={() => handleGenderToggle('boys')}
                                    className="w-4 h-4 cursor-pointer accent-[#A9BFA2] border-gray-300 dark:border-zinc-600 rounded focus:ring-[#A9BFA2] focus:ring-2"
                                />
                                <span className="text-gray-600 dark:text-zinc-400 group-hover:text-gray-900 dark:group-hover:text-zinc-100 transition-colors">
                                    Niños
                                </span>
                            </label>
                            <label className="flex items-center text-sm gap-2 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={selectedGenders.includes('girls')}
                                    onChange={() => handleGenderToggle('girls')}
                                    className="w-4 h-4 cursor-pointer accent-[#A9BFA2] border-gray-300 dark:border-zinc-600 rounded focus:ring-[#A9BFA2] focus:ring-2"
                                />
                                <span className="text-gray-600 dark:text-zinc-400 group-hover:text-gray-900 dark:group-hover:text-zinc-100 transition-colors">
                                    Niñas
                                </span>
                            </label>
                        </div>
                    </div>
                )}

                {/* Categories */}
                <div className="mb-8">
                    <h3 className="font-semibold mb-3 text-gray-900 dark:text-zinc-200">
                        Categorías
                    </h3>
                    <ul className="text-sm text-gray-600 dark:text-zinc-400 space-y-2">
                        {categories.map((category, index) => (
                            <li
                                key={index}
                                className="cursor-pointer hover:text-gray-900 dark:hover:text-zinc-100 transition-colors"
                            >
                                {category}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Price Range Slider */}
                <div>
                    <h3 className="font-semibold mb-3 text-gray-900 dark:text-zinc-200">
                        Comprar por precio
                    </h3>

                    <div className="space-y-6">
                        {/* Price Display */}
                        <div className="flex items-center justify-between text-sm font-medium">
                            <span className="text-gray-900 dark:text-zinc-100">
                                {formatPrice(priceRange[0])}
                            </span>
                            <span className="text-gray-900 dark:text-zinc-100">
                                {formatPrice(priceRange[1])}
                            </span>
                        </div>

                        {/* Dual Range Slider */}
                        <div className="relative h-2 w-full">
                            {/* Track Background */}
                            <div className="absolute w-full h-full bg-gray-200 dark:bg-zinc-700 rounded-full"></div>

                            {/* Selected Range (Green) */}
                            <div
                                className="absolute h-full bg-[#A9BFA2] rounded-full"
                                style={{
                                    left: `${((priceRange[0] - 100) / 9900) * 100}%`,
                                    right: `${100 - ((priceRange[1] - 100) / 9900) * 100}%`
                                }}
                            ></div>

                            {/* Min Input */}
                            <input
                                type="range"
                                min="100"
                                max="10000"
                                step="100"
                                value={priceRange[0]}
                                onChange={(e) => {
                                    const val = Math.min(Number(e.target.value), priceRange[1] - 100);
                                    setPriceRange([val, priceRange[1]]);
                                }}
                                className="absolute w-full h-full appearance-none bg-transparent pointer-events-none z-20 slider-thumb-custom"
                            />

                            {/* Max Input */}
                            <input
                                type="range"
                                min="100"
                                max="10000"
                                step="100"
                                value={priceRange[1]}
                                onChange={(e) => {
                                    const val = Math.max(Number(e.target.value), priceRange[0] + 100);
                                    setPriceRange([priceRange[0], val]);
                                }}
                                className="absolute w-full h-full appearance-none bg-transparent pointer-events-none z-20 slider-thumb-custom"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                .slider-thumb-custom::-webkit-slider-thumb {
                    pointer-events: auto;
                    appearance: none;
                    width: 20px;
                    height: 20px;
                    background: white;
                    border: 3px solid #A9BFA2;
                    border-radius: 50%;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    transition: transform 0.1s;
                }

                .slider-thumb-custom::-moz-range-thumb {
                    pointer-events: auto;
                    width: 20px;
                    height: 20px;
                    background: white;
                    border: 3px solid #A9BFA2;
                    border-radius: 50%;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    transition: transform 0.1s;
                    box-sizing: border-box;
                }

                .slider-thumb-custom::-webkit-slider-thumb:hover {
                    transform: scale(1.1);
                }

                .slider-thumb-custom::-moz-range-thumb:hover {
                    transform: scale(1.1);
                }
            `}</style>
        </aside>
    );
}
