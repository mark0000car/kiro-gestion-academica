"""
Pruebas unitarias para los endpoints de docentes.
Usa SQLite en memoria — no requiere PostgreSQL.
"""
import pytest


# ---------------------------------------------------------------------------
# Datos de prueba reutilizables
# ---------------------------------------------------------------------------

DOCENTE_VALIDO = {
    "nombre": "Carlos Martínez",
    "email": "carlos.martinez@ejemplo.com",
    "especialidad": "Matemáticas",
}

DOCENTE_2 = {
    "nombre": "Laura Gómez",
    "email": "laura.gomez@ejemplo.com",
    "especialidad": "Física",
}


# ===========================================================================
# POST /teachers/
# ===========================================================================

class TestCrearDocente:

    def test_crear_docente_exitoso(self, client):
        resp = client.post("/teachers/", json=DOCENTE_VALIDO)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == DOCENTE_VALIDO["nombre"]
        assert data["email"] == DOCENTE_VALIDO["email"]
        assert data["especialidad"] == DOCENTE_VALIDO["especialidad"]
        assert data["activo"] is True
        assert "id" in data
        assert "fecha_creacion" in data

    def test_crear_docente_email_duplicado(self, client):
        client.post("/teachers/", json=DOCENTE_VALIDO)
        duplicado = {**DOCENTE_VALIDO, "especialidad": "Química"}
        resp = client.post("/teachers/", json=duplicado)
        assert resp.status_code == 409
        assert "email" in resp.json()["detail"].lower()

    def test_crear_docente_especialidad_duplicada(self, client):
        client.post("/teachers/", json=DOCENTE_VALIDO)
        duplicado = {**DOCENTE_VALIDO, "email": "otro@ejemplo.com"}
        resp = client.post("/teachers/", json=duplicado)
        assert resp.status_code == 409
        assert "especialidad" in resp.json()["detail"].lower()

    def test_crear_docente_email_invalido(self, client):
        datos = {**DOCENTE_VALIDO, "email": "no-es-un-email"}
        resp = client.post("/teachers/", json=datos)
        assert resp.status_code == 422

    def test_crear_docente_nombre_faltante(self, client):
        datos = {k: v for k, v in DOCENTE_VALIDO.items() if k != "nombre"}
        resp = client.post("/teachers/", json=datos)
        assert resp.status_code == 422

    def test_crear_docente_nombre_vacio(self, client):
        datos = {**DOCENTE_VALIDO, "nombre": "   "}
        resp = client.post("/teachers/", json=datos)
        assert resp.status_code == 422

    def test_crear_docente_especialidad_faltante(self, client):
        datos = {k: v for k, v in DOCENTE_VALIDO.items() if k != "especialidad"}
        resp = client.post("/teachers/", json=datos)
        assert resp.status_code == 422

    def test_crear_docente_especialidad_vacia(self, client):
        datos = {**DOCENTE_VALIDO, "especialidad": "   "}
        resp = client.post("/teachers/", json=datos)
        assert resp.status_code == 422

    def test_crear_docente_campos_faltantes(self, client):
        resp = client.post("/teachers/", json={})
        assert resp.status_code == 422

    def test_crear_docente_respuesta_tiene_campos_requeridos(self, client):
        resp = client.post("/teachers/", json=DOCENTE_VALIDO)
        data = resp.json()
        for campo in ("id", "nombre", "email", "especialidad", "activo", "fecha_creacion"):
            assert campo in data, f"Campo '{campo}' ausente en la respuesta"


# ===========================================================================
# GET /teachers/{id}
# ===========================================================================

class TestObtenerDocente:

    def test_obtener_docente_existente(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.get(f"/teachers/{creado['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == creado["id"]

    def test_obtener_docente_no_existente(self, client):
        resp = client.get("/teachers/99999")
        assert resp.status_code == 404
        assert "no encontrado" in resp.json()["detail"].lower()

    def test_obtener_docente_id_invalido(self, client):
        resp = client.get("/teachers/abc")
        assert resp.status_code == 422

    def test_obtener_docente_datos_completos(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.get(f"/teachers/{creado['id']}").json()
        assert resp["nombre"] == DOCENTE_VALIDO["nombre"]
        assert resp["email"] == DOCENTE_VALIDO["email"]
        assert resp["especialidad"] == DOCENTE_VALIDO["especialidad"]


# ===========================================================================
# GET /teachers/
# ===========================================================================

class TestListarDocentes:

    def test_listar_sin_docentes(self, client):
        resp = client.get("/teachers/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["docentes"] == []

    def test_listar_con_docentes(self, client):
        client.post("/teachers/", json=DOCENTE_VALIDO)
        client.post("/teachers/", json=DOCENTE_2)
        resp = client.get("/teachers/")
        data = resp.json()
        assert data["total"] == 2
        assert len(data["docentes"]) == 2

    def test_listar_paginacion(self, client):
        for i in range(5):
            client.post("/teachers/", json={
                "nombre": f"Docente {i}",
                "email": f"docente{i}@ejemplo.com",
                "especialidad": f"Materia {i}",
            })
        resp = client.get("/teachers/?pagina=1&por_pagina=2")
        data = resp.json()
        assert data["total"] == 5
        assert len(data["docentes"]) == 2
        assert data["por_pagina"] == 2
        assert data["pagina"] == 1

    def test_listar_segunda_pagina(self, client):
        for i in range(4):
            client.post("/teachers/", json={
                "nombre": f"Docente {i}",
                "email": f"doc{i}@ejemplo.com",
                "especialidad": f"Materia {i}",
            })
        resp = client.get("/teachers/?pagina=2&por_pagina=2")
        data = resp.json()
        assert len(data["docentes"]) == 2

    def test_listar_filtro_activo(self, client):
        client.post("/teachers/", json=DOCENTE_VALIDO)
        resp = client.get("/teachers/?activo=true")
        data = resp.json()
        assert all(d["activo"] for d in data["docentes"])

    def test_listar_por_pagina_maximo_100(self, client):
        resp = client.get("/teachers/?por_pagina=200")
        assert resp.status_code == 422

    def test_listar_pagina_invalida(self, client):
        resp = client.get("/teachers/?pagina=0")
        assert resp.status_code == 422

    def test_listar_estructura_respuesta(self, client):
        resp = client.get("/teachers/")
        data = resp.json()
        for campo in ("total", "pagina", "por_pagina", "docentes"):
            assert campo in data


# ===========================================================================
# PUT /teachers/{id}
# ===========================================================================

class TestActualizarDocente:

    def test_actualizar_nombre(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"nombre": "Carlos López"})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Carlos López"

    def test_actualizar_email(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"email": "nuevo@ejemplo.com"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "nuevo@ejemplo.com"

    def test_actualizar_especialidad(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"especialidad": "Química"})
        assert resp.status_code == 200
        assert resp.json()["especialidad"] == "Química"

    def test_actualizar_estado_inactivo(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"activo": False})
        assert resp.status_code == 200
        assert resp.json()["activo"] is False

    def test_actualizar_multiples_campos(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={
            "nombre": "Carlos López",
            "especialidad": "Biología",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Carlos López"
        assert data["especialidad"] == "Biología"

    def test_actualizar_no_existente(self, client):
        resp = client.put("/teachers/99999", json={"nombre": "Nadie"})
        assert resp.status_code == 404

    def test_actualizar_email_duplicado(self, client):
        doc1 = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        client.post("/teachers/", json=DOCENTE_2)
        resp = client.put(f"/teachers/{doc1['id']}", json={"email": DOCENTE_2["email"]})
        assert resp.status_code == 409

    def test_actualizar_especialidad_duplicada(self, client):
        doc1 = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        client.post("/teachers/", json=DOCENTE_2)
        resp = client.put(f"/teachers/{doc1['id']}", json={"especialidad": DOCENTE_2["especialidad"]})
        assert resp.status_code == 409

    def test_actualizar_cuerpo_vacio(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == DOCENTE_VALIDO["nombre"]
        assert resp.json()["email"] == DOCENTE_VALIDO["email"]

    def test_actualizar_email_invalido(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"email": "no-valido"})
        assert resp.status_code == 422

    def test_actualizar_nombre_vacio(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.put(f"/teachers/{creado['id']}", json={"nombre": "   "})
        assert resp.status_code == 422

    def test_actualizar_preserva_otros_campos(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        client.put(f"/teachers/{creado['id']}", json={"nombre": "Nuevo Nombre"})
        obtenido = client.get(f"/teachers/{creado['id']}").json()
        assert obtenido["email"] == DOCENTE_VALIDO["email"]
        assert obtenido["especialidad"] == DOCENTE_VALIDO["especialidad"]


# ===========================================================================
# DELETE /teachers/{id}
# ===========================================================================

class TestEliminarDocente:

    def test_eliminar_existente(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        resp = client.delete(f"/teachers/{creado['id']}")
        assert resp.status_code == 200
        assert "eliminado" in resp.json()["mensaje"].lower()

    def test_eliminar_ya_no_existe(self, client):
        creado = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        client.delete(f"/teachers/{creado['id']}")
        resp = client.get(f"/teachers/{creado['id']}")
        assert resp.status_code == 404

    def test_eliminar_no_existente(self, client):
        resp = client.delete("/teachers/99999")
        assert resp.status_code == 404

    def test_eliminar_reduce_total(self, client):
        doc1 = client.post("/teachers/", json=DOCENTE_VALIDO).json()
        client.post("/teachers/", json=DOCENTE_2)
        client.delete(f"/teachers/{doc1['id']}")
        data = client.get("/teachers/").json()
        assert data["total"] == 1

    def test_eliminar_id_invalido(self, client):
        resp = client.delete("/teachers/abc")
        assert resp.status_code == 422
