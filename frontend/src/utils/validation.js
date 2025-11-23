/**
 * Validation utilities for form fields
 */

/**
 * Validates if a value is not empty
 */
export const required = (value, fieldName = 'Este campo') => {
    if (!value || !value.trim()) {
        return `${fieldName} es requerido`
    }
    return null
}

/**
 * Validates phone number format
 * Accepts formats like: +52 662 122 29 43, 6621222943, +526621222943
 */
export const validatePhone = (value) => {
    if (!value) return 'El teléfono es requerido'

    const cleanPhone = value.replace(/\s/g, '')
    if (!/^\+?\d{10,}$/.test(cleanPhone)) {
        return 'Formato de teléfono inválido (mínimo 10 dígitos)'
    }
    return null
}

/**
 * Validates postal code (5 digits)
 */
export const validatePostalCode = (value) => {
    if (!value) return 'El código postal es requerido'

    if (!/^\d{5}$/.test(value.trim())) {
        return 'Código postal debe tener 5 dígitos'
    }
    return null
}

/**
 * Validates email format
 */
export const validateEmail = (value) => {
    if (!value) return 'El correo electrónico es requerido'

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value.trim())) {
        return 'Formato de correo electrónico inválido'
    }
    return null
}

/**
 * Validates credit card number (Simple check)
 */
export const validateCardNumber = (value) => {
    if (!value) return 'El número de tarjeta es requerido'

    // Removed strict validation as requested
    // Just check if it has at least some digits
    const cleanNumber = value.replace(/\s/g, '')
    if (cleanNumber.length < 4) {
        return 'Número de tarjeta inválido'
    }

    return null
}

/**
 * Validates card expiry date (MM/YY format)
 */
export const validateExpiryDate = (value) => {
    if (!value) return 'La fecha de expiración es requerida'

    if (!/^\d{2}\/\d{2}$/.test(value)) {
        return 'Formato inválido (MM/YY)'
    }

    const [month, year] = value.split('/').map(Number)
    if (month < 1 || month > 12) {
        return 'Mes inválido'
    }

    const now = new Date()
    const currentYear = now.getFullYear() % 100
    const currentMonth = now.getMonth() + 1

    if (year < currentYear || (year === currentYear && month < currentMonth)) {
        return 'Tarjeta expirada'
    }

    return null
}

/**
 * Validates CVV (3-4 digits)
 */
export const validateCVV = (value) => {
    if (!value) return 'El CVV es requerido'

    if (!/^\d{3,4}$/.test(value)) {
        return 'CVV inválido (3-4 dígitos)'
    }
    return null
}

/**
 * Validates a complete payment card object
 */
export const validatePaymentCard = (card) => {
    const errors = {}

    const nameError = required(card.cardholderName, 'El nombre del titular')
    if (nameError) errors.cardholderName = nameError

    const cardNumberError = validateCardNumber(card.cardNumber)
    if (cardNumberError) errors.cardNumber = cardNumberError

    const expiryError = validateExpiryDate(card.expiryDate)
    if (expiryError) errors.expiryDate = expiryError

    const cvvError = validateCVV(card.cvv)
    if (cvvError) errors.cvv = cvvError

    return errors
}

/**
 * Validates a complete address object
 * Returns an object with field names as keys and error messages as values
 */
export const validateAddress = (address) => {
    const errors = {}

    const nameError = required(address.name, 'El nombre')
    if (nameError) errors.name = nameError

    const phoneError = validatePhone(address.phone)
    if (phoneError) errors.phone = phoneError

    const streetError = required(address.street, 'La calle')
    if (streetError) errors.street = streetError

    const detailsError = required(address.details, 'Los detalles')
    if (detailsError) errors.details = detailsError

    const cityError = required(address.city, 'La ciudad')
    if (cityError) errors.city = cityError

    const postalCodeError = validatePostalCode(address.postalCode)
    if (postalCodeError) errors.postalCode = postalCodeError

    return errors
}

/**
 * Checks if an errors object has any errors
 */
export const hasErrors = (errors) => {
    return Object.keys(errors).length > 0
}
