"""
Configuración del motor SQLAlchemy y el pool de conexiones.
Proporciona la sesión de base de datos como dependencia de FastAPI.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool

from app.config import settings


# ---------------------------------------------------------------------------
# Motor principal con pool de conexiones
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.database_url,
    # Pool de conexiones: máximo 10 conexiones activas, 20 en cola de espera
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # Verifica que la conexión esté viva antes de usarla
    pool_recycle=1800,        # Recicla conexiones cada 30 minutos
    echo=False,               # Poner en True para depurar SQL generado
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------------------------
# Clase base para los modelos ORM
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Dependencia de FastAPI: inyecta y cierra la sesión automáticamente
# ---------------------------------------------------------------------------
def get_db():
    """Generador que provee una sesión de BD y la cierra al terminar el request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Utilidad: verificar la conexión a la BD
# ---------------------------------------------------------------------------
def verificar_conexion() -> bool:
    """Devuelve True si la conexión a PostgreSQL es exitosa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
