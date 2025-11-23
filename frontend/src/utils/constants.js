/**
 * Application-wide constants
 */

// Address Component Constants
export const ADDRESS_CARD_WIDTH = '252px'
export const ADDRESS_CARD_MIN_HEIGHT = '200px'
export const ADDRESS_CONTAINER_MAX_WIDTH = '900px'
export const POSTAL_CODE_LENGTH = 5
export const MIN_PHONE_DIGITS = 10

// Modal Constants
export const MODAL_MAX_WIDTH = '500px'
export const MODAL_MAX_HEIGHT = '90vh'

// Colors (matching design system)
export const COLORS = {
    primary: 'rgb(169,191,162)',
    primaryHover: 'rgb(159,181,152)',
    primaryLight: 'rgb(240,244,239)',
    textPrimary: 'rgb(77,76,76)',
    error: 'rgb(239,68,68)', // red-500
}

// Form Field Placeholders
export const PLACEHOLDERS = {
    name: 'Ej: Juan Pérez',
    phone: 'Ej: +52 662 123 4567',
    street: 'Ej: Av. Reforma',
    details: 'Ej: #123 Col. Centro',
    city: 'Ej: Hermosillo, Sonora, México',
    postalCode: '5 dígitos',
    email: 'correo@ejemplo.com',
    cardholderName: 'Ej: Juan Pérez',
    cardNumber: '1234 5678 9012 3456',
    expiryDate: 'MM/YY',
    cvv: '123',
}

// Validation Messages
export const VALIDATION_MESSAGES = {
    required: (field) => `${field} es requerido`,
    invalidPhone: 'Formato de teléfono inválido',
    invalidPostalCode: 'Código postal debe tener 5 dígitos',
    invalidEmail: 'Formato de correo electrónico inválido',
}
