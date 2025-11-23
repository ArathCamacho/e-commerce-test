/**
 * Reusable Form Input Component
 * @param {string} label - Input label
 * @param {string} type - Input type (default: 'text')
 * @param {string} value - Input value
 * @param {function} onChange - Change handler
 * @param {string} error - Error message
 * @param {string} placeholder - Placeholder text
 * @param {number} maxLength - Maximum character length
 * @param {object} rest - Additional props
 */
export function FormInput({
    label,
    type = 'text',
    value,
    onChange,
    error,
    placeholder,
    maxLength,
    ...rest
}) {
    return (
        <div>
            <label className="block text-sm font-light text-[rgb(77,76,76)] dark:text-zinc-400 mb-2">
                {label}
            </label>
            <input
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                maxLength={maxLength}
                className={`w-full h-[35px] px-3 border ${error
                        ? 'border-red-500'
                        : 'border-gray-300 dark:border-zinc-700'
                    } bg-white dark:bg-zinc-900 text-black dark:text-zinc-100 text-base font-light focus:outline-none focus:border-[rgb(169,191,162)] transition-colors`}
                {...rest}
            />
            {error && (
                <p className="text-red-500 text-xs mt-1">{error}</p>
            )}
        </div>
    )
}
