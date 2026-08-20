"""
Fixtures compartidas para todas las pruebas.

- db_session : sesión SQLite en memoria (pruebas unitarias, sin PostgreSQL).
- client     : TestClient de FastAPI usando la sesión en memoria.
- db_postgres: sesión real a PostgreSQL (pruebas de integración).
- client_pg  : TestClient usando la conexión real a PostgreSQL.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# Base de datos SQLite en memoria (pruebas unitarias)
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    """Crea y destruye el esquema SQLite por cada test."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient que inyecta la sesión SQLite en memoria."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Base de datos PostgreSQL real (pruebas de integración)
# Se saltan automáticamente si la BD no está disponible.
# ---------------------------------------------------------------------------
from app.config import settings  # noqa: E402

PG_URL = settings.database_url


def _pg_available() -> bool:
    try:
        from sqlalchemy import create_engine, text
        eng = create_engine(PG_URL, pool_pre_ping=True)
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


pg_available = _pg_available()
skip_if_no_pg = pytest.mark.skipif(
    not pg_available, reason="PostgreSQL no disponible"
)

engine_pg = create_engine(PG_URL, pool_pre_ping=True) if pg_available else None
PGSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_pg) if pg_available else None


@pytest.fixture(scope="function")
def db_postgres():
    """Sesión real a PostgreSQL. Se omite si no hay conexión disponible."""
    if not pg_available:
        pytest.skip("PostgreSQL no disponible")
    Base.metadata.create_all(bind=engine_pg)
    session = PGSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Limpia solo los datos del test, mantiene la tabla
        from app.models import Estudiante
        session2 = PGSessionLocal()
        session2.query(Estudiante).delete()
        session2.commit()
        session2.close()


@pytest.fixture(scope="function")
def client_pg(db_postgres):
    """TestClient conectado a PostgreSQL real."""
    def override_get_db():
        try:
            yield db_postgres
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
