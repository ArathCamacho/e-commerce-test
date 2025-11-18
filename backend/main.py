from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.sistema import router as sistema_router
from database import engine, Base

# Crear las tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="Ecommerce API",
    description="API REST para sistema distribuido de ecommerce",
    version="1.0.0"
)

# Configurar CORS (permite peticiones desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(sistema_router, prefix="/api", tags=["Sistema"])

@app.get("/")
async def root():
    return {
        "message": "Bienvenido al API de Ecommerce",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)