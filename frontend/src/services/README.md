# Documentación de Servicios API

Esta documentación explica cómo usar la capa de servicios para comunicarte con el backend.

## Configuración Inicial

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto frontend basado en `.env.example`:

```bash
# Copia el archivo de ejemplo
cp .env.example .env
```

Edita `.env` y configura la URL de tu backend:

```env
VITE_API_BASE_URL=http://localhost:3000/api
```

### 2. Instalación de Dependencias

Si aún no lo has hecho, asegúrate de tener `axios` instalado:

```bash
npm install axios
```

## Estructura de Servicios

```
src/services/
├── api.js                    # Configuración base (axios, interceptors)
├── authService.js            # Autenticación
├── productService.js         # Productos
├── categoryService.js        # Categorías
├── cartService.js            # Carrito
├── orderService.js           # Órdenes
├── userService.js            # Usuario
├── addressService.js         # Direcciones
├── paymentService.js         # Métodos de pago
├── checkoutService.js        # Checkout
└── likeService.js            # Likes/Favoritos
```

## Ejemplos de Uso

### Autenticación (`authService.js`)

```javascript
import authService from '../services/authService'

// Login
const handleLogin = async (email, password) => {
  try {
    const response = await authService.login(email, password)
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    // Redirigir al usuario
  } catch (error) {
    console.error('Error:', error.response?.data?.message)
  }
}

// Registro
const handleRegister = async (userData) => {
  try {
    const response = await authService.register(userData)
    // Manejar respuesta
  } catch (error) {
    console.error('Error:', error)
  }
}

// Logout
const handleLogout = async () => {
  await authService.logout()
  // Redirigir a login
}
```

### Productos (`productService.js`)

```javascript
import productService from '../services/productService'
import { useState, useEffect } from 'react'

function ProductList() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await productService.getFeaturedProducts(8)
        setProducts(response.data)
      } catch (error) {
        console.error('Error loading products:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchProducts()
  }, [])

  // Render productos...
}

// Buscar productos
const searchProducts = async (query) => {
  const response = await productService.searchProducts(query)
  return response.data
}

// Obtener producto por ID
const getProduct = async (id) => {
  const response = await productService.getProductById(id)
  return response.data
}
```

### Carrito (`cartService.js`)

```javascript
import cartService from '../services/cartService'

// Agregar al carrito
const addProductToCart = async (product) => {
  try {
    const response = await cartService.addToCart({
      productId: product.id,
      quantity: 1,
      size: 'M',
      color: 'Rojo'
    })
    console.log('Carrito actualizado:', response.data)
  } catch (error) {
    console.error('Error:', error)
  }
}

// Obtener carrito
const loadCart = async () => {
  const response = await cartService.getCart()
  return response.data
}

// Actualizar cantidad
const updateItemQuantity = async (itemId, quantity) => {
  await cartService.updateCartItem(itemId, quantity)
}

// Eliminar item
const removeItem = async (itemId) => {
  await cartService.removeFromCart(itemId)
}
```

### Órdenes (`orderService.js`)

```javascript
import orderService from '../services/orderService'

// Obtener órdenes del usuario
const loadOrders = async () => {
  try {
    const response = await orderService.getOrders()
    setOrders(response.data)
  } catch (error) {
    console.error('Error loading orders:', error)
  }
}

// Obtener detalle de orden
const getOrderDetails = async (orderId) => {
  const response = await orderService.getOrderById(orderId)
  return response.data
}

// Cancelar orden
const cancelOrder = async (orderId) => {
  await orderService.cancelOrder(orderId, 'Cambio de opinión')
}
```

### Direcciones (`addressService.js`)

```javascript
import addressService from '../services/addressService'

// Obtener todas las direcciones
const loadAddresses = async () => {
  const response = await addressService.getAddresses()
  return response.data
}

// Crear nueva dirección
const createNewAddress = async (addressData) => {
  const response = await addressService.createAddress({
    firstName: 'Juan',
    lastName: 'Pérez',
    address1: 'Calle Principal 123',
    address2: 'Apto 456',
    city: 'Ciudad de México',
    state: 'CDMX',
    postalCode: '01234',
    country: 'México',
    phone: '5551234567',
    isDefault: true
  })
  return response.data
}

// Actualizar dirección
const updateAddress = async (id, data) => {
  await addressService.updateAddress(id, data)
}

// Eliminar dirección
const deleteAddress = async (id) => {
  await addressService.deleteAddress(id)
}

// Establecer como predeterminada
const setDefaultAddress = async (id) => {
  await addressService.setDefaultAddress(id)
}
```

### Métodos de Pago (`paymentService.js`)

```javascript
import paymentService from '../services/paymentService'

// Obtener métodos de pago
const loadPaymentMethods = async () => {
  const response = await paymentService.getPaymentMethods()
  return response.data
}

// Agregar método de pago
const addPaymentMethod = async (paymentData) => {
  const response = await paymentService.addPaymentMethod({
    cardNumber: '4111111111111111',
    cardholderName: 'Juan Pérez',
    expirationDate: '12/25',
    cvv: '123',
    billingAddressId: 1,
    isDefault: true
  })
  return response.data
}

// Eliminar método de pago
const deletePaymentMethod = async (id) => {
  await paymentService.deletePaymentMethod(id)
}
```

### Checkout (`checkoutService.js`)

```javascript
import checkoutService from '../services/checkoutService'

// Obtener datos de checkout
const loadCheckoutData = async () => {
  const response = await checkoutService.getCheckoutData()
  return response.data
}

// Actualizar info de envío
const updateShipping = async (addressId, method) => {
  await checkoutService.updateShippingInfo({
    addressId,
    shippingMethod: method // 'standard', 'express', 'overnight'
  })
}

// Procesar pago y completar orden
const completeCheckout = async (paymentData) => {
  try {
    const response = await checkoutService.processPayment({
      paymentMethodId: 1,
      shippingAddressId: 2,
      billingAddressId: 2,
      shippingMethod: 'standard'
    })
    console.log('Orden creada:', response.data)
    // Redirigir a página de confirmación
  } catch (error) {
    console.error('Error al procesar pago:', error)
  }
}
```

### Likes/Favoritos (`likeService.js`)

```javascript
import likeService from '../services/likeService'

// Dar like a un producto
const likeProduct = async (productId) => {
  await likeService.likeProduct(productId)
}

// Quitar like
const unlikeProduct = async (productId) => {
  await likeService.unlikeProduct(productId)
}

// Toggle like
const toggleProductLike = async (productId) => {
  const response = await likeService.toggleLike(productId)
  return response.data.isLiked
}

// Obtener productos con like
const loadLikedProducts = async () => {
  const response = await likeService.getLikedProducts()
  return response.data
}
```

## Manejo de Errores

Todos los servicios usan try-catch para manejo de errores:

```javascript
import productService from '../services/productService'

const loadProducts = async () => {
  try {
    const response = await productService.getProducts()
    setProducts(response.data)
  } catch (error) {
    // El error ya fue registrado en el interceptor de axios
    // Aquí puedes mostrar un mensaje al usuario
    if (error.response) {
      // Error de respuesta del servidor
      console.error('Error del servidor:', error.response.data.message)
      setError(error.response.data.message)
    } else if (error.request) {
      // Error de red - no hubo respuesta
      console.error('Error de red')
      setError('No se pudo conectar con el servidor')
    } else {
      // Otro tipo de error
      console.error('Error:', error.message)
      setError('Ocurrió un error inesperado')
    }
  }
}
```

## Autenticación Automática

El archivo `api.js` incluye interceptores que:

1. **Agregan automáticamente** el token JWT a todas las peticiones:
```javascript
// No necesitas hacer esto manualmente:
headers: {
  'Authorization': `Bearer ${token}`
}

// El interceptor lo hace automáticamente
```

2. **Redirigen al login** si el token expira (código 401):
```javascript
// Si recibes un 401, automáticamente:
// - Se limpia el localStorage
// - Se redirige a /login
```

## Componentes Refactorizados

Los siguientes componentes ya están integrados con los servicios:

1. **`Login.jsx`** - Usa `authService` para login real
2. **`FeaturedProducts.jsx`** - Usa `productService` para cargar productos
3. **`OrdersList.jsx`** - Usa `orderService` para cargar órdenes
4. **`CartContext.jsx`** - Usa `cartService` para todas las operaciones del carrito

## Próximos Pasos

Para integrar los servicios en otros componentes:

1. Importa el servicio necesario
2. Usa `async/await` en funciones de tu componente
3. Maneja estados de loading y error
4. Actualiza el estado local con los datos del backend

Ejemplo de patrón recomendado:

```javascript
import { useState, useEffect } from 'react'
import myService from '../services/myService'

function MyComponent() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const response = await myService.getData()
      setData(response.data)
      setError(null)
    } catch (error) {
      console.error('Error:', error)
      setError('No se pudieron cargar los datos')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Cargando...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      {/* Renderizar data */}
    </div>
  )
}
```

## Notas Importantes

- Todos los servicios devuelven una **Promise**
- Los servicios no lanzan errores, debes capturarlos con `try-catch`
- La respuesta siempre está en `response.data`
- El token se guarda y envía automáticamente
- Los servicios funcionan tanto autenticado como no autenticado (donde aplique)
