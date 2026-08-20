"""
Pruebas unitarias para los endpoints de estudiantes.
Usa SQLite en memoria — no requiere PostgreSQL.
"""
import pytest


# ---------------------------------------------------------------------------
# Datos de prueba reutilizables
# ---------------------------------------------------------------------------

ESTUDIANTE_VALIDO = {
    "nombre": "Ana García",
    "direccion": "Calle 10 # 20-30, Bogotá",
    "numero_documento": "1020304050",
    "email": "ana.garcia@ejemplo.com",
}

ESTUDIANTE_2 = {
    "nombre": "Carlos Pérez",
    "direccion": "Av. Siempre Viva 742",
    "numero_documento": "9876543210",
    "email": "carlos.perez@ejemplo.com",
}


# ===========================================================================
# POST /students/
# ===========================================================================

class TestCrearEstudiante:

    def test_crear_estudiante_exitoso(self, client):
        resp = client.post("/students/", json=ESTUDIANTE_VALIDO)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == ESTUDIANTE_VALIDO["nombre"]
        assert data["email"] == ESTUDIANTE_VALIDO["email"]
        assert data["activo"] is True
        assert "id" in data
        assert "fecha_creacion" in data

    def test_crear_estudiante_email_duplicado(self, client):
        client.post("/students/", json=ESTUDIANTE_VALIDO)
        duplicado = {**ESTUDIANTE_VALIDO, "numero_documento": "9999999"}
        resp = client.post("/students/", json=duplicado)
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower()

    def test_crear_estudiante_documento_duplicado(self, client):
        client.post("/students/", json=ESTUDIANTE_VALIDO)
        duplicado = {**ESTUDIANTE_VALIDO, "email": "otro@ejemplo.com"}
        resp = client.post("/students/", json=duplicado)
        assert resp.status_code == 409
        assert "documento" in resp.json()["detail"].lower()

    def test_crear_estudiante_email_invalido(self, client):
        datos = {**ESTUDIANTE_VALIDO, "email": "no-es-un-email"}
        resp = client.post("/students/", json=datos)
        assert resp.status_code == 422

    def test_crear_estudiante_nombre_faltante(self, client):
        datos = {k: v for k, v in ESTUDIANTE_VALIDO.items() if k != "nombre"}
        resp = client.post("/students/", json=datos)
        assert resp.status_code == 422

    def test_crear_estudiante_nombre_vacio(self, client):
        datos = {**ESTUDIANTE_VALIDO, "nombre": "   "}
        resp = client.post("/students/", json=datos)
        assert resp.status_code == 422

    def test_crear_estudiante_documento_formato_invalido(self, client):
        datos = {**ESTUDIANTE_VALIDO, "numero_documento": "AB"}  # muy corto
        resp = client.post("/students/", json=datos)
        assert resp.status_code == 422

    def test_crear_estudiante_campos_faltantes(self, client):
        resp = client.post("/students/", json={})
        assert resp.status_code == 422

    def test_crear_estudiante_respuesta_tiene_campos_requeridos(self, client):
        resp = client.post("/students/", json=ESTUDIANTE_VALIDO)
        data = resp.json()
        for campo in ("id", "nombre", "direccion", "numero_documento", "email",
                      "activo", "fecha_creacion"):
            assert campo in data, f"Campo '{campo}' ausente en la respuesta"


# ===========================================================================
# GET /students/{id}
# ===========================================================================

class TestObtenerEstudiante:

    def test_obtener_estudiante_existente(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.get(f"/students/{creado['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == creado["id"]

    def test_obtener_estudiante_no_existente(self, client):
        resp = client.get("/students/99999")
        assert resp.status_code == 404
        assert "no encontrado" in resp.json()["detail"].lower()

    def test_obtener_estudiante_id_invalido(self, client):
        resp = client.get("/students/abc")
        assert resp.status_code == 422

    def test_obtener_estudiante_datos_completos(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.get(f"/students/{creado['id']}").json()
        assert resp["nombre"] == ESTUDIANTE_VALIDO["nombre"]
        assert resp["email"] == ESTUDIANTE_VALIDO["email"]
        assert resp["numero_documento"] == ESTUDIANTE_VALIDO["numero_documento"]


# ===========================================================================
# GET /students/
# ===========================================================================

class TestListarEstudiantes:

    def test_listar_sin_estudiantes(self, client):
        resp = client.get("/students/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["estudiantes"] == []

    def test_listar_con_estudiantes(self, client):
        client.post("/students/", json=ESTUDIANTE_VALIDO)
        client.post("/students/", json=ESTUDIANTE_2)
        resp = client.get("/students/")
        data = resp.json()
        assert data["total"] == 2
        assert len(data["estudiantes"]) == 2

    def test_listar_paginacion(self, client):
        for i in range(5):
            client.post("/students/", json={
                "nombre": f"Estudiante {i}",
                "direccion": f"Calle {i}",
                "numero_documento": f"DOC{i:04d}",
                "email": f"estudiante{i}@ejemplo.com",
            })
        resp = client.get("/students/?pagina=1&por_pagina=2")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["estudiantes"]) == 2
        assert data["por_pagina"] == 2
        assert data["pagina"] == 1

    def test_listar_segunda_pagina(self, client):
        for i in range(4):
            client.post("/students/", json={
                "nombre": f"Estudiante {i}",
                "direccion": f"Calle {i}",
                "numero_documento": f"DOC{i:04d}",
                "email": f"est{i}@ejemplo.com",
            })
        resp = client.get("/students/?pagina=2&por_pagina=2")
        data = resp.json()
        assert len(data["estudiantes"]) == 2

    def test_listar_filtro_activo(self, client):
        client.post("/students/", json=ESTUDIANTE_VALIDO)
        resp = client.get("/students/?activo=true")
        data = resp.json()
        assert all(e["activo"] for e in data["estudiantes"])

    def test_listar_por_pagina_maximo_100(self, client):
        # La API limita a 100 aunque se pidan más
        resp = client.get("/students/?por_pagina=200")
        assert resp.status_code == 422  # Query param le=100

    def test_listar_pagina_invalida(self, client):
        resp = client.get("/students/?pagina=0")
        assert resp.status_code == 422

    def test_listar_estructura_respuesta(self, client):
        resp = client.get("/students/")
        data = resp.json()
        for campo in ("total", "pagina", "por_pagina", "estudiantes"):
            assert campo in data


# ===========================================================================
# PUT /students/{id}
# ===========================================================================

class TestActualizarEstudiante:

    def test_actualizar_nombre(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={"nombre": "Ana López"})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Ana López"

    def test_actualizar_email(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={"email": "nuevo@ejemplo.com"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "nuevo@ejemplo.com"

    def test_actualizar_estado_inactivo(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={"activo": False})
        assert resp.status_code == 200
        assert resp.json()["activo"] is False

    def test_actualizar_multiples_campos(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={
            "nombre": "Ana López",
            "direccion": "Nueva Calle 99",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Ana López"
        assert data["direccion"] == "Nueva Calle 99"

    def test_actualizar_no_existente(self, client):
        resp = client.put("/students/99999", json={"nombre": "Nadie"})
        assert resp.status_code == 404

    def test_actualizar_email_duplicado(self, client):
        est1 = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        client.post("/students/", json=ESTUDIANTE_2)
        resp = client.put(f"/students/{est1['id']}", json={"email": ESTUDIANTE_2["email"]})
        assert resp.status_code == 409

    def test_actualizar_cuerpo_vacio(self, client):
        # Req 4.3: empty body is a no-op → 200 with unchanged student
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == ESTUDIANTE_VALIDO["nombre"]
        assert resp.json()["email"] == ESTUDIANTE_VALIDO["email"]

    def test_actualizar_email_invalido(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.put(f"/students/{creado['id']}", json={"email": "no-valido"})
        assert resp.status_code == 422

    def test_actualizar_preserva_otros_campos(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        client.put(f"/students/{creado['id']}", json={"nombre": "Nuevo Nombre"})
        obtenido = client.get(f"/students/{creado['id']}").json()
        assert obtenido["email"] == ESTUDIANTE_VALIDO["email"]
        assert obtenido["numero_documento"] == ESTUDIANTE_VALIDO["numero_documento"]


# ===========================================================================
# DELETE /students/{id}
# ===========================================================================

class TestEliminarEstudiante:

    def test_eliminar_existente(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        resp = client.delete(f"/students/{creado['id']}")
        assert resp.status_code == 200
        assert "eliminado" in resp.json()["mensaje"].lower()

    def test_eliminar_ya_no_existe(self, client):
        creado = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        client.delete(f"/students/{creado['id']}")
        resp = client.get(f"/students/{creado['id']}")
        assert resp.status_code == 404

    def test_eliminar_no_existente(self, client):
        resp = client.delete("/students/99999")
        assert resp.status_code == 404

    def test_eliminar_reduce_total(self, client):
        est1 = client.post("/students/", json=ESTUDIANTE_VALIDO).json()
        client.post("/students/", json=ESTUDIANTE_2)
        client.delete(f"/students/{est1['id']}")
        data = client.get("/students/").json()
        assert data["total"] == 1

    def test_eliminar_id_invalido(self, client):
        resp = client.delete("/students/abc")
        assert resp.status_code == 422


# ===========================================================================
# Endpoints de utilidad
# ===========================================================================

class TestUtilidad:

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data

    def test_health_check(self, client):
        # Con SQLite el health devuelve error de BD, pero la API responde
        resp = client.get("/health")
        assert resp.status_code in (200, 503)

    def test_docs_disponibles(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "openapi" in data
        assert "paths" in data

