# Implementation Plan: Gestión de Docentes (`teacher-management`)

## Overview

Extender el sistema existente de Gestión Académica con un módulo de **Gestión de Docentes** que expone cinco endpoints CRUD bajo el prefijo `/teachers`. El módulo sigue exactamente los mismos patrones arquitectónicos del módulo de estudiantes: FastAPI + SQLAlchemy 2.0 + Pydantic v2. Las tareas están ordenadas de menor a mayor dependencia: modelo de datos → validación → acceso a datos → endpoints → registro → pruebas → documentación.

---

## Tasks

- [x] 1. Agregar dependencia `hypothesis` y modelo ORM `Docente`
  - [x] 1.1 Agregar `hypothesis>=6.100.0` al archivo `requirements.txt`
    - Insertar la línea debajo de `email-validator` para mantener el orden
    - _Requirements: 9.1_

  - [x] 1.2 Agregar la clase `Docente(Base)` en `app/models.py`
    - Definir `__tablename__ = "docentes"`
    - Columnas con `Mapped` / `mapped_column` (SQLAlchemy 2.0): `id` (Integer PK autoincrement), `nombre` (String 200, not null), `email` (String 254, not null, unique, index), `especialidad` (String 200, not null, unique, index), `fecha_creacion` (DateTime timezone=True, not null, server_default=func.now()), `activo` (Boolean, not null, default=True)
    - Agregar el modelo junto a `Estudiante` sin modificar la clase existente
    - _Requirements: 7.1, 1.1, 1.2_

- [x] 2. Agregar schemas Pydantic v2 para Docente
  - [x] 2.1 Agregar `DocenteBase`, `DocenteCreate`, `DocenteUpdate`, `DocenteResponse` y `DocentePaginado` en `app/schemas.py`
    - `DocenteBase`: campos `nombre: str`, `email: EmailStr`, `especialidad: str`; `field_validator` para `nombre` (strip, rechaza vacío, rechaza > 200 chars) y para `especialidad` (strip, rechaza vacío, rechaza > 200 chars)
    - `DocenteCreate`: hereda `DocenteBase` sin campos adicionales
    - `DocenteUpdate`: todos los campos opcionales (`nombre?`, `email?`, `especialidad?`, `activo?`); mismos validadores condicionales (`if v is not None`)
    - `DocenteResponse`: hereda `DocenteBase`, agrega `id: int`, `activo: bool`, `fecha_creacion: datetime`; `model_config = {"from_attributes": True}`
    - `DocentePaginado`: campos `total: int`, `pagina: int`, `por_pagina: int`, `docentes: list[DocenteResponse]`
    - Agregar los schemas al final del archivo sin modificar los existentes de `Estudiante`
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 4.7, 4.9, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ]* 2.2 Escribir prueba de propiedad 2: Rechazo universal de campos en blanco
    - **Property 2: Rechazo universal de campos en blanco**
    - **Validates: Requirements 1.5, 8.1, 8.4**
    - Usar `@given(blanco=st.from_regex(r"^\s+$", fullmatch=True))` con `@settings(max_examples=100)`
    - Enviar el string como `nombre` y como `especialidad` en `POST /teachers/`; ambos deben resultar en HTTP 422
    - Verificar que ningún docente persiste (GET lista debe devolver `total=0`)

  - [ ]* 2.3 Escribir prueba de propiedad 3: Rechazo universal de emails con formato inválido
    - **Property 3: Rechazo universal de emails con formato inválido**
    - **Validates: Requirements 1.6, 8.3**
    - Generar strings inválidos (sin `@`, sin punto en dominio, longitud > 254): `st.one_of(st.text(max_size=20).filter(lambda s: "@" not in s), st.just("sinpunto@dominio"), st.text(min_size=255, max_size=260))`
    - Enviar en `POST /teachers/` y en `PUT /teachers/{id}` (sobre docente existente); ambos deben devolver HTTP 422

- [x] 3. Agregar funciones CRUD para Docente en `app/crud.py`
  - [x] 3.1 Implementar `crear_docente`, `obtener_docente_por_id`, `obtener_docente_por_email`, `obtener_docente_por_especialidad`, `listar_docentes`, `actualizar_docente` y `eliminar_docente`
    - `crear_docente(db, datos: DocenteCreate) -> Docente`: crea instancia, `db.add`, `db.commit`, `db.refresh`; puede lanzar `IntegrityError`
    - `obtener_docente_por_id(db, id) -> Optional[Docente]`: `db.get(Docente, id)`
    - `obtener_docente_por_email(db, email) -> Optional[Docente]`: `select` con `where`
    - `obtener_docente_por_especialidad(db, especialidad) -> Optional[Docente]`: `select` con `where`
    - `listar_docentes(db, pagina, por_pagina, solo_activos) -> tuple[list[Docente], int]`: paginación con `offset/limit`, filtro opcional por `activo`, orden por `id` ascendente
    - `actualizar_docente(db, docente, datos: DocenteUpdate) -> Docente`: `model_dump(exclude_unset=True)`, `setattr` por campo, convierte `email` a `str`; puede lanzar `IntegrityError`
    - `eliminar_docente(db, docente) -> None`: `db.delete`, `db.commit`
    - Agregar las funciones al final del archivo sin modificar las existentes de `Estudiante`
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 3.7, 3.10, 4.1, 4.6, 5.1, 5.3_

  - [ ]* 3.2 Escribir prueba de propiedad 6: Actualización parcial preserva campos no enviados
    - **Property 6: Actualización parcial preserva campos no enviados**
    - **Validates: Requirements 4.1, 4.6**
    - Crear un docente base; para cualquier subconjunto no vacío de campos válidos enviados en `PUT /teachers/{id}`, verificar que los campos NO incluidos conservan exactamente los valores previos
    - Usar `st.fixed_dictionaries` o `st.sampled_from` para elegir qué campos actualizar

- [x] 4. Crear el router `app/routers/teachers.py`
  - [x] 4.1 Implementar los cinco endpoints CRUD y helpers en `app/routers/teachers.py`
    - Crear `router = APIRouter(prefix="/teachers", tags=["Docentes"])`
    - Helper `_get_or_404(db, docente_id)`: llama `crud.obtener_docente_por_id`; lanza `HTTP 404` con mensaje `"Docente con id={id} no encontrado."`
    - Helper `_handle_integrity_error(exc)`: inspecciona `str(exc.orig).lower()`; devuelve `HTTP 409` con mensaje diferenciado para `"email"` y `"especialidad"`
    - `POST /teachers/` → `HTTP 201`, captura `IntegrityError`
    - `GET /teachers/` → `HTTP 200`, parámetros `pagina` (≥1, default 1), `por_pagina` (1–100, default 10), `activo: Optional[bool]`; devuelve `DocentePaginado`
    - `GET /teachers/{docente_id}` → `HTTP 200` (incluyendo `activo=false`)
    - `PUT /teachers/{docente_id}` → `HTTP 200`; body vacío `{}` es no-op, captura `IntegrityError`
    - `DELETE /teachers/{docente_id}` → `HTTP 200` con mensaje `{"mensaje": "Docente con id={id} eliminado exitosamente."}`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.9, 3.10, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2_

- [ ] 5. Registrar el router y actualizar `conftest.py`
  - [-] 5.1 Agregar `teachers.router` en `app/main.py`
    - Agregar `from app.routers import teachers` junto a la importación de `students`
    - Agregar `app.include_router(teachers.router)` debajo de `app.include_router(students.router)`
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

  - [-] 5.2 Actualizar el fixture `db_postgres` en `tests/conftest.py`
    - En la sección de limpieza, agregar `from app.models import Docente` y `session2.query(Docente).delete()` antes del commit
    - Mantener el `session2.query(Estudiante).delete()` existente sin modificarlo
    - _Requirements: 9.6, 9.7_

- [~] 6. Checkpoint — Verificar que el servidor inicia y los endpoints responden
  - Asegurarse de que `app/main.py`, `app/models.py`, `app/schemas.py`, `app/crud.py` y `app/routers/teachers.py` no tienen errores de importación. Ejecutar `pytest tests/test_students.py` para confirmar que el módulo de estudiantes no se rompió. Preguntar al usuario si hay dudas antes de continuar.

- [ ] 7. Crear el script de migración SQL e `init_db.py`
  - [-] 7.1 Crear `migrations/create_teachers_table.sql`
    - DDL idempotente con `CREATE TABLE IF NOT EXISTS docentes` con columnas `id SERIAL PRIMARY KEY`, `nombre VARCHAR(200) NOT NULL`, `email VARCHAR(254) NOT NULL`, `especialidad VARCHAR(200) NOT NULL`, `fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `activo BOOLEAN NOT NULL DEFAULT TRUE`
    - Constraints nombrados: `CONSTRAINT uq_docentes_email UNIQUE (email)`, `CONSTRAINT uq_docentes_especialidad UNIQUE (especialidad)`
    - Índices con `CREATE INDEX IF NOT EXISTS idx_docentes_email ON docentes (email)` y `CREATE INDEX IF NOT EXISTS idx_docentes_especialidad ON docentes (especialidad)`
    - Comentarios `COMMENT ON TABLE` y `COMMENT ON COLUMN` para cada columna
    - _Requirements: 7.1, 7.2, 7.5_

  - [-] 7.2 Crear `init_db.py` en la raíz del proyecto
    - Leer `migrations/create_teachers_table.sql` con `pathlib.Path`
    - Ejecutar con `engine.begin()` y `conn.execute(text(sql))`
    - Reportar éxito en stdout con `print`; capturar excepciones y reportar en `sys.stderr` con `sys.exit(1)`
    - _Requirements: 7.3, 7.4, 7.5_

- [ ] 8. Crear las pruebas unitarias en `tests/test_teachers.py`
  - [~] 8.1 Implementar los casos de prueba de ejemplo para `POST /teachers/`
    - Caso de éxito HTTP 201: verificar `id`, `activo=true`, `fecha_creacion`, `nombre`, `email`, `especialidad`
    - Caso HTTP 409 por email duplicado: mensaje debe contener `"email"`
    - Caso HTTP 409 por especialidad duplicada: mensaje debe contener `"especialidad"`
    - Caso HTTP 422 por campos requeridos ausentes
    - Caso HTTP 422 por `nombre` vacío / solo espacios
    - Caso HTTP 422 por `especialidad` vacía / solo espacios
    - Caso HTTP 422 por `email` con formato inválido
    - _Requirements: 9.1, 9.2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [~] 8.2 Implementar los casos de prueba de ejemplo para `GET /teachers/{id}` y `GET /teachers/`
    - `GET /teachers/{id}`: caso 200 con datos correctos, caso 200 con `activo=false`, caso 404, caso 422 con id no entero
    - `GET /teachers/`: caso 200 lista vacía (`total=0`, `docentes=[]`), caso 200 con paginación (verificar `total`, `pagina`, `por_pagina`, longitud de `docentes`), caso filtro `activo=true`, caso filtro `activo=false`, caso 422 con `por_pagina>100`, caso 422 con `pagina<1`
    - Verificar que `docentes` está ordenado por `id` ascendente en el caso paginado
    - _Requirements: 9.1, 9.2, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.9, 3.10_

  - [~] 8.3 Implementar los casos de prueba de ejemplo para `PUT /teachers/{id}` y `DELETE /teachers/{id}`
    - `PUT /teachers/{id}`: caso 200 con actualización parcial (solo `nombre`), caso 200 con body vacío `{}` (no-op, sin cambios), caso 404, caso 409 por email duplicado, caso 409 por especialidad duplicada, caso 422 por email inválido
    - `DELETE /teachers/{id}`: caso 200 con mensaje que contiene el id, verificar que `GET /teachers/{id}` devuelve 404 tras la eliminación, verificar que no aparece en `GET /teachers/`, caso 404, caso 422 con id no entero
    - _Requirements: 9.1, 9.2, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3_

  - [ ]* 8.4 Escribir prueba de propiedad 1: Round-trip de creación y lectura
    - **Property 1: Round-trip de creación y lectura**
    - **Validates: Requirements 1.1, 1.2, 2.1**
    - `@given(nombre=st.text(min_size=1, max_size=200).filter(lambda s: s.strip()), especialidad=st.text(min_size=1, max_size=200).filter(lambda s: s.strip()), email=st.emails())`
    - `@settings(max_examples=100)`; usar `assume(resp.status_code == 201)` para descartar conflictos de unicidad
    - Verificar que `GET /teachers/{id}` devuelve `activo=true`, el mismo `nombre`, `email`, `especialidad`, y `id > 0`

  - [ ]* 8.5 Escribir prueba de propiedad 4: El filtro de estado es exhaustivo
    - **Property 4: El filtro de estado es exhaustivo**
    - **Validates: Requirements 3.7**
    - Crear N docentes con valores `activo` mixtos (algunos actualizados a `activo=false` vía `PUT`)
    - Verificar que `GET /teachers?activo=true` devuelve únicamente docentes con `activo=true`
    - Verificar que `GET /teachers?activo=false` devuelve únicamente docentes con `activo=false`

  - [ ]* 8.6 Escribir prueba de propiedad 5: Ordenamiento determinista por ID
    - **Property 5: Ordenamiento determinista por ID**
    - **Validates: Requirements 3.10**
    - `@given(n=st.integers(min_value=2, max_value=10))` con `@settings(max_examples=50)`
    - Crear N docentes en orden arbitrario; verificar que `[d["id"] for d in resp.json()["docentes"]] == sorted(ids)`

  - [ ]* 8.7 Escribir prueba de propiedad 7: La eliminación hace el recurso inaccesible
    - **Property 7: La eliminación hace el recurso inaccesible**
    - **Validates: Requirements 5.1, 5.3**
    - Para cualquier docente creado con datos válidos, eliminar con `DELETE /teachers/{id}`, luego verificar que `GET /teachers/{id}` devuelve 404 y que el docente no aparece en `GET /teachers/?por_pagina=100`

- [ ] 9. Crear las pruebas de integración en `tests/test_teachers_integration.py`
  - [ ]* 9.1 Implementar pruebas de integración contra PostgreSQL real
    - Decorar todos los casos con `@skip_if_no_pg` (importar de `conftest.py`)
    - Usar el fixture `client_pg`
    - Al menos un caso de éxito por endpoint: `POST /teachers/` (201), `GET /teachers/{id}` (200), `GET /teachers/` (200 con paginación), `PUT /teachers/{id}` (200 parcial), `DELETE /teachers/{id}` (200)
    - Verificar que los constraints de unicidad (`email`, `especialidad`) producen 409 a nivel de PostgreSQL real
    - _Requirements: 9.6, 9.7_

- [~] 10. Checkpoint — Ejecutar la suite de pruebas unitarias completa
  - Ejecutar `pytest tests/test_teachers.py -v` y verificar que todos los casos pasan en menos de 60 segundos y sin errores de conexión a PostgreSQL. Preguntar al usuario si hay dudas antes de continuar.

- [ ] 11. Actualizar documentación y `requirements.txt`
  - [~] 11.1 Actualizar el `README.md` con la documentación del módulo de docentes
    - Sección con los cinco endpoints: método HTTP, ruta, descripción, códigos de respuesta éxito y error
    - Sección con el modelo de datos `Docente`: campos, tipos, longitudes máximas, restricciones de unicidad, valores por defecto
    - Ejemplos `curl` con al menos un ejemplo por endpoint (datos válidos y respuesta esperada)
    - Variables de entorno (reutiliza las mismas de estudiantes: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DATABASE_URL`)
    - Comandos exactos: `python init_db.py` y `pytest tests/test_teachers.py` con resultado esperado
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [~] 12. Checkpoint final — Verificar integridad completa del módulo
  - Ejecutar `pytest tests/test_students.py tests/test_teachers.py -v` para confirmar que ambos módulos pasan sin regresiones. Preguntar al usuario si hay dudas antes de cerrar la implementación.

---

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido. Sin embargo, las propiedades de corrección (Property 1–7) validan invariantes universales que el módulo debe mantener.
- Cada tarea modifica o crea un archivo específico; el orden garantiza que nunca se importa un símbolo que aún no existe.
- Los checkpoints (tareas 6, 10, 12) permiten detectar regresiones de forma temprana antes de continuar.
- El fixture `db_postgres` limpia tanto `Docente` como `Estudiante` para garantizar aislamiento en las pruebas de integración.
- Las pruebas de propiedades con `hypothesis` pueden descubrir edge cases no cubiertos por ejemplos concretos; se recomienda ejecutarlas al menos antes del merge.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "3.1"] },
    { "id": 3, "tasks": ["3.2", "4.1"] },
    { "id": 4, "tasks": ["5.1", "5.2", "7.1", "7.2"] },
    { "id": 5, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 6, "tasks": ["8.4", "8.5", "8.6", "8.7", "9.1"] },
    { "id": 7, "tasks": ["11.1"] }
  ]
}
```
