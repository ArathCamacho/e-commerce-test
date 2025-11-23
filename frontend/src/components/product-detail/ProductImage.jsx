export function ProductImage({ image, name }) {
    return (
        <div className="w-full lg:w-[40%] h-full bg-gray-100 dark:bg-zinc-800">
            <img
                src={image}
                alt={name}
                className="w-full h-full object-cover object-center"
            />
        </div>
    )
}
