# 🚀 Guía de Despliegue en Vercel

Esta guía te llevará paso a paso para desplegar tu frontend de e-commerce en Vercel de forma gratuita.

---

## 📋 PASO 1: Preparar tu Proyecto

### 1.1 Verificar que tu frontend funciona localmente

Antes de subir, asegúrate que corre sin errores:

```bash
cd frontend
npm run dev
```

Si funciona bien, continúa.

### 1.2 Verificar la URL de tu API

✅ **Ya está configurado**: Tu archivo `src/services/apiservice.js` ya apunta a tu backend de Render:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://e-commerce-test-mm6o.onrender.com/api";
```

### 1.3 Hacer build de prueba

Verifica que tu proyecto compile sin errores:

```bash
npm run build
```

Si sale todo bien, verás una carpeta `dist` creada. ¡Perfecto!

---

## 📤 PASO 2: Subir tu Código a GitHub

### 2.1 Verificar Git (si ya tienes repositorio)

Si ya tienes Git inicializado, verifica el estado:

```bash
git status
```

### 2.2 Inicializar Git (si NO lo has hecho)

Desde la carpeta `frontend`:

```bash
git init
git add .
git commit -m "Preparar frontend para deploy en Vercel"
```

### 2.3 Crear repositorio en GitHub

1. Ve a: https://github.com/
2. Haz clic en el **"+"** arriba a la derecha
3. Selecciona **"New repository"**
4. **Nombre**: `ecommerce-frontend` (o el que quieras)
5. **Importante**: Déjalo **Público** (Vercel requiere repos públicos en plan gratuito)
6. **NO** marques "Add README"
7. Haz clic en **"Create repository"**

### 2.4 Conectar tu proyecto local con GitHub

GitHub te mostrará comandos, copia y pega estos (ajusta con tu usuario):

```bash
git remote add origin https://github.com/TU-USUARIO/ecommerce-frontend.git
git branch -M main
git push -u origin main
```

> **Nota**: Si ya tienes un remote configurado, usa:
> ```bash
> git remote set-url origin https://github.com/TU-USUARIO/ecommerce-frontend.git
> ```

---

## 🚀 PASO 3: Desplegar en Vercel

### 3.1 Crear cuenta en Vercel

1. Ve a: https://vercel.com/
2. Haz clic en **"Sign Up"**
3. Selecciona **"Continue with GitHub"**
4. Autoriza a Vercel a acceder a tu GitHub
5. Completa el registro

### 3.2 Importar tu proyecto

1. En el dashboard de Vercel, haz clic en **"Add New..."**
2. Selecciona **"Project"**
3. Busca tu repositorio `ecommerce-frontend`
4. Haz clic en **"Import"**

### 3.3 Configurar el proyecto

Vercel detectará automáticamente que es un proyecto Vite + React. Verifica que esté así:

```
Framework Preset: Vite
Root Directory: ./
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

**¡NO CAMBIES NADA!** Vercel lo detecta solo.

### 3.4 Variables de Entorno (Opcional)

Si quieres sobrescribir la URL del API, agrega en **Environment Variables**:

```
VITE_API_BASE_URL = https://e-commerce-test-mm6o.onrender.com/api
```

Pero no es necesario porque ya está en el código.

### 3.5 Desplegar

1. Haz clic en **"Deploy"**
2. Espera 1-2 minutos (verás logs en tiempo real)
3. Cuando termine, verás: **"🎉 Congratulations!"**

### 3.6 Ver tu sitio

Vercel te dará una URL como:

```
https://ecommerce-frontend-abc123.vercel.app
```

¡Haz clic y verás tu e-commerce en vivo! 🎉

---

## 🔧 PASO 4: Configurar CORS en tu Backend

**MUY IMPORTANTE**: Para que tu frontend pueda hablar con tu backend, necesitas configurar CORS.

### 4.1 Actualizar tu backend

Abre tu archivo principal de FastAPI (probablemente `main.py`) y agrega:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Desarrollo local
        "https://tu-frontend.vercel.app",  # ⚠️ Reemplaza con tu URL de Vercel
        "https://*.vercel.app"  # Permite todos los subdominios de Vercel
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resto de tu código...
```

**⚠️ IMPORTANTE**: Reemplaza `https://tu-frontend.vercel.app` con la URL real que te dio Vercel.

### 4.2 Hacer push del cambio

```bash
git add .
git commit -m "Configurar CORS para Vercel"
git push
```

Render detectará el cambio y re-desplegará automáticamente (2-3 minutos).

---

## 🔄 PASO 5: Actualizaciones Automáticas

Cada vez que hagas cambios en tu frontend:

```bash
# 1. Editar código
# 2. Guardar cambios
git add .
git commit -m "Descripción del cambio"
git push
```

**No necesitas hacer nada más.** Vercel detecta el push y actualiza tu sitio solo en 1-2 minutos.

---

## 📝 PASO 6: Personalizar Dominio (OPCIONAL)

### 6.1 Cambiar el nombre del proyecto

1. En Vercel, ve a tu proyecto
2. Haz clic en **"Settings"**
3. En **"Domains"**, agrega un subdominio personalizado:
   ```
   vandentials-store.vercel.app
   ```
4. Haz clic en **"Add"**

Ahora tu sitio será accesible en esa URL más bonita.

---

## 🎯 CHECKLIST FINAL

Antes de presentar tu proyecto, verifica:

- [ ] Frontend corre localmente sin errores (`npm run dev`)
- [ ] La URL de la API apunta a Render (no localhost)
- [ ] El código está en GitHub
- [ ] El sitio está desplegado en Vercel
- [ ] Puedes acceder a tu sitio desde cualquier navegador
- [ ] CORS está configurado en el backend
- [ ] Puedes ver el catálogo de productos
- [ ] Puedes verificar disponibilidad (POST funciona)
- [ ] Las imágenes se ven correctamente
- [ ] El routing funciona (refrescar página no da 404)

---

## 🚨 TROUBLESHOOTING

### ❌ Error: "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT"

**Causa**: Tienes un bloqueador de anuncios activo.  
**Solución**: Desactívalo temporalmente o agrega tu sitio a la lista blanca.

### ❌ Error: "Access to fetch has been blocked by CORS policy"

**Causa**: No configuraste CORS en tu backend.  
**Solución**: Ve al **PASO 4** y configura CORS correctamente.

### ❌ Error: "404 Not Found" al refrescar página

**Causa**: Vercel necesita configuración especial para React Router.  
**Solución**: ✅ **Ya está resuelto** - El archivo `vercel.json` ya está configurado.

### ❌ Error: "Cannot find module..."

**Causa**: Falta instalar dependencias.  
**Solución**: En Vercel, ve a **Settings → Environment Variables** y agrega:
```
NODE_VERSION = 18
```

### ❌ Las imágenes no cargan

**Causa**: Las URLs de las imágenes en tu BD no son válidas.  
**Solución**: Verifica las URLs en Neon Console (deben empezar con `https://`).

### ❌ Error: "Build failed" en Vercel

**Causa**: Errores de compilación o dependencias faltantes.  
**Solución**:
1. Revisa los logs de build en Vercel
2. Verifica que `npm run build` funcione localmente
3. Asegúrate que todas las dependencias estén en `package.json`

---

## 📊 RESUMEN VISUAL

```
┌─────────────────────────────────────────────────┐
│  1. Preparar proyecto                           │
│     - Verificar build local                     │
│     - Configuración ya lista                    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. Subir a GitHub                              │
│     - git init, add, commit                     │
│     - Crear repo público                        │
│     - git push                                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. Desplegar en Vercel                         │
│     - Sign up con GitHub                        │
│     - Importar proyecto                         │
│     - Deploy (automático)                       │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  4. Configurar CORS en Backend                  │
│     - Agregar middleware CORS                   │
│     - Permitir origen de Vercel                 │
│     - Push a Render                             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  ✅ Sistema completo en producción              │
│     Backend: Render                             │
│     Frontend: Vercel                            │
│     Base de Datos: Neon                         │
└─────────────────────────────────────────────────┘
```

---

## ⏱️ TIEMPO ESTIMADO

- **Configuración inicial**: 5 minutos (ya hecho con archivos creados)
- **Subir a GitHub**: 5 minutos
- **Despliegue en Vercel**: 5 minutos
- **Configurar CORS**: 5 minutos
- **Total**: ~20 minutos

---

## 🎓 PARA TU REPORTE

Agrega esto a tu diagrama de despliegue:

```
Componente: Frontend (Vercel)
Responsabilidad: Renderizar interfaz y comunicarse con backend
Tecnología: React + Vite, desplegado en Vercel PaaS
Protocolo: HTTPS
URL: https://tu-proyecto.vercel.app
Características:
  - Despliegue automático desde GitHub
  - CDN global para baja latencia
  - SSL/TLS automático
  - Actualizaciones en tiempo real
```

---

## 📁 Archivos Creados

Este deployment incluye los siguientes archivos de configuración:

1. **`vercel.json`**: Configuración de routing y headers de seguridad
2. **`.env.production`**: Variables de entorno para producción
3. **`DEPLOYMENT.md`**: Esta guía completa

---

## 🔗 Enlaces Útiles

- [Documentación de Vercel](https://vercel.com/docs)
- [Guía de Vite en Vercel](https://vercel.com/docs/frameworks/vite)
- [Configuración de CORS en FastAPI](https://fastapi.tiangolo.com/tutorial/cors/)

---

¡Listo! Ahora tienes todo lo necesario para desplegar tu frontend en Vercel. 🚀
