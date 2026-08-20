"""
Pruebas de integración — requieren PostgreSQL real.
Se saltan automáticamente si la BD no está disponible.

Ejecutar solo integración:
    pytest tests/test_integration.py -v
"""
import pytest

from tests.conftest import skip_if_no_pg

ESTUDIANTE = {
    "nombre": "Laura Martínez",
    "direccion": "Cra 5 # 15-20, Medellín",
    "numero_documento": "INT-001",
    "email": "laura.martinez@integracion.com",
}

ESTUDIANTE_2 = {
    "nombre": "Pedro Ruiz",
    "direccion": "Calle 80 # 10-05, Cali",
    "numero_documento": "INT-002",
    "email": "pedro.ruiz@integracion.com",
}


# ===========================================================================
# Conexión a PostgreSQL
# ===========================================================================

@skip_if_no_pg
def test_conexion_postgresql(db_postgres):
    """Verifica que la conexión real a PostgreSQL funciona."""
    from sqlalchemy import text
    result = db_postgres.execute(text("SELECT 1")).scalar()
    assert result == 1


@skip_if_no_pg
def test_tabla_estudiantes_existe(db_postgres):
    """Verifica que la tabla 'estudiantes' existe en la BD."""
    from sqlalchemy import inspect
    inspector = inspect(db_postgres.get_bind())
    tablas = inspector.get_table_names()
    assert "estudiantes" in tablas


# ===========================================================================
# CRUD completo sobre PostgreSQL real
# ===========================================================================

@skip_if_no_pg
def test_pg_crear_y_obtener_estudiante(client_pg):
    resp = client_pg.post("/students/", json=ESTUDIANTE)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == ESTUDIANTE["email"]

    obtenido = client_pg.get(f"/students/{data['id']}").json()
    assert obtenido["id"] == data["id"]
    assert obtenido["nombre"] == ESTUDIANTE["nombre"]


@skip_if_no_pg
def test_pg_email_duplicado(client_pg):
    client_pg.post("/students/", json=ESTUDIANTE)
    duplicado = {**ESTUDIANTE, "numero_documento": "INT-DUP"}
    resp = client_pg.post("/students/", json=duplicado)
    assert resp.status_code == 409


@skip_if_no_pg
def test_pg_documento_duplicado(client_pg):
    client_pg.post("/students/", json=ESTUDIANTE)
    duplicado = {**ESTUDIANTE, "email": "otro.email@integracion.com"}
    resp = client_pg.post("/students/", json=duplicado)
    assert resp.status_code == 409


@skip_if_no_pg
def test_pg_listar_paginado(client_pg):
    client_pg.post("/students/", json=ESTUDIANTE)
    client_pg.post("/students/", json=ESTUDIANTE_2)
    resp = client_pg.get("/students/?pagina=1&por_pagina=1")
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["estudiantes"]) == 1


@skip_if_no_pg
def test_pg_actualizar_estudiante(client_pg):
    creado = client_pg.post("/students/", json=ESTUDIANTE).json()
    resp = client_pg.put(f"/students/{creado['id']}", json={"nombre": "Laura González"})
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Laura González"


@skip_if_no_pg
def test_pg_eliminar_estudiante(client_pg):
    creado = client_pg.post("/students/", json=ESTUDIANTE).json()
    resp = client_pg.delete(f"/students/{creado['id']}")
    assert resp.status_code == 200
    assert client_pg.get(f"/students/{creado['id']}").status_code == 404


@skip_if_no_pg
def test_pg_health_check_con_bd_real(client_pg):
    resp = client_pg.get("/health")
    assert resp.status_code == 200
    assert resp.json()["base_de_datos"] == "ok"


@skip_if_no_pg
def test_pg_actualizacion_parcial_no_modifica_otros_campos(client_pg):
    creado = client_pg.post("/students/", json=ESTUDIANTE).json()
    client_pg.put(f"/students/{creado['id']}", json={"direccion": "Nueva Dirección 123"})
    obtenido = client_pg.get(f"/students/{creado['id']}").json()
    assert obtenido["email"] == ESTUDIANTE["email"]
    assert obtenido["numero_documento"] == ESTUDIANTE["numero_documento"]
