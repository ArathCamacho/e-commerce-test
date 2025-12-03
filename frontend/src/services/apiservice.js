import axios from "axios";

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8003/api";

// Crear instancia de axios con configuración base
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // 60 segundos (Render puede tardar al iniciar)
});

// ==================== PRODUCTOS Y CATÁLOGO ====================

export const ProductoService = {
  // Verificar disponibilidad de producto
  verificarDisponibilidad: async (idProducto, cantidadSolicitada) => {
    const response = await apiClient.post(
      "/productos/verificar-disponibilidad",
      {
        id_producto: idProducto,
        cantidad_solicitada: cantidadSolicitada,
      }
    );
    return response.data;
  },

  // Obtener catálogo completo (GET)
  obtenerCatalogo: async (storeId = 1, category = null) => {
    const params = { store_id: storeId };
    if (category) params.category = category;

    const response = await apiClient.get("/catalogo", { params });
    return response.data;
  },

  // Obtener catálogo completo (POST)
  obtenerCatalogoPost: async (storeId = 1, category = null) => {
    const response = await apiClient.post("/catalogo", {
      store_id: storeId,
      category: category,
    });
    return response.data;
  },

  // Obtener catálogo sin filtros
  obtenerCatalogoCompleto: async () => {
    const response = await apiClient.get("/catalogo/all");
    return response.data;
  },

  // Obtener producto por ID (Simulado filtrando del catálogo)
  obtenerPorId: async (idProducto) => {
    // Primero intentamos obtener del catálogo completo
    const response = await apiClient.get("/catalogo/all");
    const productos = response.data.productos || response.data || [];
    const producto = productos.find(p => p.id == idProducto);
    
    if (producto) return producto;
    
    // Si no está, lanzamos error
    throw new Error("Producto no encontrado");
  },
};

// ==================== CLIENTES ====================

export const ClienteService = {
  // Registrar nuevo cliente
  registrar: async (datosCliente) => {
    const response = await apiClient.post("/clientes/registro", datosCliente);
    return response.data;
  },

  // Login de cliente
  login: async (email, password) => {
    const response = await apiClient.post("/clientes/login", {
      correo: email,
      contrasena: password,
    });
    return response.data;
  },

  // Obtener información de cliente
  obtener: async (idCliente) => {
    const response = await apiClient.get(`/clientes/${idCliente}`);
    return response.data;
  },
};

// ==================== DIRECCIONES ====================

export const DireccionService = {
  // Agregar dirección a un cliente
  agregar: async (idCliente, datosDireccion) => {
    const response = await apiClient.post(
      `/clientes/${idCliente}/direcciones`,
      datosDireccion
    );
    return response.data;
  },

  // Obtener direcciones de un cliente
  obtener: async (idCliente) => {
    const response = await apiClient.get(`/clientes/${idCliente}/direcciones`);
    return response.data;
  },
};

// ==================== CARRITO ====================

export const CarritoService = {
  // Agregar producto al carrito
  agregar: async (idCliente, idProducto, cantidad, color = null, talla = null) => {
    const response = await apiClient.post("/carrito/agregar", {
      id_cliente: idCliente,
      id_producto: idProducto,
      cantidad: cantidad,
      color: color,
      talla: talla
    });
    return response.data;
  },

  // Obtener carrito de un cliente
  obtener: async (idCliente) => {
    const response = await apiClient.get(`/carrito/${idCliente}`);
    return response.data;
  },

  // Eliminar item del carrito
  eliminarItem: async (idItem, idCliente) => {
    const response = await apiClient.delete(`/carrito/item/${idItem}`, {
      params: { id_cliente: idCliente },
    });
    return response.data;
  },

  // Vaciar carrito completo
  vaciar: async (idCliente) => {
    const response = await apiClient.delete(`/carrito/${idCliente}/vaciar`);
    return response.data;
  },
};

// ==================== PEDIDOS ====================

export const PedidoService = {
  // Crear pedido desde carrito
  crear: async (idCliente, idDireccion) => {
    const response = await apiClient.post("/pedidos/crear", null, {
      params: {
        id_cliente: idCliente,
        id_direccion: idDireccion,
      },
    });
    return response.data;
  },

  // Obtener información de un pedido
  obtener: async (idPedido) => {
    const response = await apiClient.get(`/pedidos/${idPedido}`);
    return response.data;
  },

  // Listar pedidos de un cliente
  listarPorCliente: async (idCliente) => {
    const response = await apiClient.get(`/pedidos/cliente/${idCliente}`);
    return response.data;
  },

  // Actualizar estado de pedido
  actualizarEstado: async (idPedido, nuevoEstado) => {
    const response = await apiClient.put(`/pedidos/${idPedido}/estado`, null, {
      params: { nuevo_estado: nuevoEstado },
    });
    return response.data;
  },
};

// ==================== PAGOS ====================

export const PagoService = {
  // Procesar pago
  procesar: async (datosPago) => {
    const response = await apiClient.post("/pagos/procesar", datosPago);
    return response.data;
  },

  // Consultar información de un pago
  consultar: async (idPago) => {
    const response = await apiClient.get(`/pagos/${idPago}`);
    return response.data;
  },

  // Consultar pagos de un pedido
  consultarPorPedido: async (idPedido) => {
    const response = await apiClient.get(`/pagos/pedido/${idPedido}`);
    return response.data;
  },
};

// ==================== ENVÍOS ====================

export const EnvioService = {
  // Mock del sistema de envíos
  crearMock: async (datosEnvio) => {
    const response = await apiClient.post("/envios/mock", datosEnvio);
    return response.data;
  },

  // Crear envío real
  crear: async (datosEnvio) => {
    const response = await apiClient.post("/envios/crear", datosEnvio);
    return response.data;
  },

  // Consultar información de un envío
  consultar: async (idEnvio) => {
    const response = await apiClient.get(`/envios/${idEnvio}`);
    return response.data;
  },

  // Consultar envío por pedido
  consultarPorPedido: async (idPedido) => {
    const response = await apiClient.get(`/envios/pedido/${idPedido}`);
    return response.data;
  },

  // Webhook para actualizaciones de envío
  actualizarWebhook: async (datosActualizacion) => {
    const response = await apiClient.post(
      "/envios/webhook",
      datosActualizacion
    );
    return response.data;
  },
};

// ==================== VENTAS EXTERNAS ====================

export const VentaExternaService = {
  // Registrar venta externa
  registrar: async (datosVenta) => {
    const response = await apiClient.post("/ventas/registrar", datosVenta);
    return response.data;
  },

  // Consultar ventas externas
  consultar: async (orderId = null) => {
    const params = orderId ? { order_id: orderId } : {};
    const response = await apiClient.get("/ventas/externas", { params });
    return response.data;
  },
};

// ==================== INTERCEPTORES (OPCIONAL) ====================

// Interceptor de respuesta para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Manejo básico de errores
    if (error.response) {
      // El servidor respondió con un código de error
      console.error("Error de respuesta:", error.response.data);
      console.error("Código de estado:", error.response.status);
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error("Error de red:", error.request);
    } else {
      // Algo pasó al configurar la petición
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);

// ==================== UTILIDADES ====================

// Función helper para guardar el cliente en localStorage
export const guardarClienteLocal = (cliente) => {
  localStorage.setItem("cliente", JSON.stringify(cliente));
};

// Función helper para obtener el cliente de localStorage
export const obtenerClienteLocal = () => {
  const cliente = localStorage.getItem("cliente");
  return cliente ? JSON.parse(cliente) : null;
};

// Función helper para limpiar el cliente de localStorage
export const limpiarClienteLocal = () => {
  localStorage.removeItem("cliente");
};

export default {
  ProductoService,
  ClienteService,
  DireccionService,
  CarritoService,
  PedidoService,
  PagoService,
  EnvioService,
  VentaExternaService,
};