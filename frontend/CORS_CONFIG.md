# Configuración de CORS para Backend FastAPI

## 📍 Ubicación
Archivo: `main.py` (o tu archivo principal de FastAPI)

## 🔧 Código a Agregar

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CONFIGURACIÓN DE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",              # Desarrollo local (Vite)
        "http://localhost:3000",              # Desarrollo local alternativo
        "https://TU-PROYECTO.vercel.app",     # ⚠️ REEMPLAZAR con tu URL de Vercel
        "https://*.vercel.app",               # Todos los subdominios de Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],                      # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                      # Permite todos los headers
)

# Resto de tu código...
```

## ⚠️ IMPORTANTE

**Después de desplegar en Vercel**, obtendrás una URL como:
```
https://ecommerce-frontend-abc123.vercel.app
```

**Reemplaza** `"https://TU-PROYECTO.vercel.app"` con tu URL real.

## 📝 Ejemplo Completo

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="E-Commerce API",
    description="API para sistema de e-commerce",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ecommerce-frontend-abc123.vercel.app",  # Tu URL real
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "E-Commerce API"}

# Tus rutas aquí...
```

## 🚀 Desplegar Cambios en Render

```bash
# 1. Agregar cambios
git add main.py

# 2. Commit
git commit -m "Configure CORS for Vercel frontend"

# 3. Push
git push
```

Render detectará el cambio y re-desplegará automáticamente (2-3 minutos).

## 🧪 Verificar CORS

Después de configurar, verifica en la consola del navegador (F12):

### ✅ Correcto
```
Status: 200 OK
Access-Control-Allow-Origin: https://tu-proyecto.vercel.app
```

### ❌ Error (CORS no configurado)
```
Access to fetch at 'https://e-commerce-test-mm6o.onrender.com/api/catalogo' 
from origin 'https://tu-proyecto.vercel.app' has been blocked by CORS policy
```

## 🔒 Seguridad

### Para Producción (Recomendado)
```python
allow_origins=[
    "https://tu-proyecto.vercel.app",  # Solo tu dominio específico
]
```

### Para Desarrollo (Más permisivo)
```python
allow_origins=[
    "http://localhost:5173",
    "https://*.vercel.app",  # Todos los subdominios
]
```

## 📚 Documentación

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

---

**Nota**: Este archivo es solo una referencia. El código debe agregarse a tu backend en Render.
