"""
Punto de entrada principal de la aplicación FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import verificar_conexion
from app.routers import students, teachers


# ---------------------------------------------------------------------------
# Lifespan: lógica de arranque / apagado
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque
    if not verificar_conexion():
        print("⚠️  ADVERTENCIA: No se pudo conectar a PostgreSQL al iniciar.")
    else:
        print("✅  Conexión a PostgreSQL establecida correctamente.")
    yield
    # Apagado (liberar recursos si fuera necesario)
    print("🔒  Aplicación apagada.")


# ---------------------------------------------------------------------------
# Instancia de la aplicación
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Sistema de Gestión de Estudiantes",
    description=(
        "API RESTful para el registro y administración de estudiantes.\n\n"
        "Permite crear, consultar, actualizar y eliminar estudiantes, "
        "con validación de datos, paginación y manejo de errores."
    ),
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "dev@gestion-academica.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware CORS (permite peticiones desde cualquier origen en desarrollo)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(students.router)
app.include_router(teachers.router)

# ---------------------------------------------------------------------------
# Endpoints de utilidad
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"], summary="Bienvenida")
def root():
    """Endpoint raíz. Confirma que la API está en línea."""
    return {
        "mensaje": "Sistema de Gestión de Estudiantes",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Root"], summary="Estado del servicio")
def health_check():
    """
    Verifica que la API y la conexión a la base de datos están operativas.
    Devuelve 200 si todo está bien, 503 si la BD no responde.
    """
    bd_ok = verificar_conexion()
    estado = {
        "api": "ok",
        "base_de_datos": "ok" if bd_ok else "error",
    }
    if not bd_ok:
        return JSONResponse(status_code=503, content=estado)
    return estado
