# Implementation Plan: Sistema de Gestión de Estudiantes

## Overview

El proyecto ya cuenta con una implementación funcional completa (`app/`, `tests/`) con 39 pruebas unitarias pasando. Las tareas de este plan se enfocan en tres áreas:

1. **Incorporar Hypothesis** como dependencia para pruebas property-based.
2. **Implementar las 10 propiedades de correctitud** definidas en el design como pruebas property-based.
3. **Cubrir los casos borde y escenarios faltantes** identificados en el design pero ausentes en el conjunto de pruebas actual.

No se construye código de aplicación desde cero; las tareas modifican archivos de prueba y de configuración existentes.

---

## Tasks

- [ ] 1. Agregar Hypothesis como dependencia de pruebas
  - Añadir `hypothesis>=6.100.0` a `requirements.txt` (versión exacta pinned)
  - Verificar que `pytest-hypothesis` no es necesario (Hypothesis se integra directamente con pytest)
  - Confirmar que `pip install -r requirements.txt` instala la nueva dependencia sin conflictos
  - _Requirements: Sección Testing Strategy del design.md_

- [ ] 2. Implementar pruebas property-based para creación de estudiante
  - [ ] 2.1 Implementar Property 1 — round-trip de creación
    - Crear `tests/test_properties.py` con estrategias Hypothesis para `EstudianteCreate`
    - Usar `@given` con `st.builds(EstudianteCreate, ...)` para generar payloads válidos
    - Verificar que `r.nombre == p.nombre`, `r.email == p.email`, `r.numero_documento == p.numero_documento`, `r.direccion == p.direccion`
    - Configurar `@settings(max_examples=100)`
    - _Requirements: 1.10_
  - [ ]* 2.2 Implementar Property 2 — invariantes de nuevo estudiante
    - Bajo el mismo fixture property-test, verificar que la respuesta tiene `activo == True` y `fecha_creacion` no nulo
    - **Property 2: New-student invariants**
    - **Validates: Requirements 1.9**
  - [ ]* 2.3 Implementar Property 3 — round-trip de serialización de schema
    - Test unitario puro (sin HTTP): dado cualquier `EstudianteCreate` válido `s`, `EstudianteCreate(**s.model_dump())` produce un objeto igual campo a campo
    - **Property 3: Schema serialization round-trip**
    - **Validates: Requirements 6.6**

- [ ] 3. Implementar pruebas property-based para consulta de estudiante
  - [ ] 3.1 Implementar Property 4 — completitud del schema de respuesta
    - Para cualquier estudiante creado, `GET /students/{id}` retorna los 7 campos requeridos con los tipos correctos
    - **Property 4: Response schema completeness**
    - **Validates: Requirements 2.1, 2.4**

- [ ] 4. Implementar pruebas property-based para paginación
  - [ ] 4.1 Implementar Property 5 — correctitud de paginación
    - Crear N estudiantes (N generado por Hypothesis), paginar con `pagina=k` y `por_pagina=m`
    - Verificar que los registros retornados corresponden exactamente al slice `(k-1)*m .. (k-1)*m + m - 1` ordenados por `id` ascendente
    - **Property 5: Pagination correctness**
    - **Validates: Requirements 3.3**
  - [ ]* 4.2 Implementar Property 6 — invariante de completitud de paginación
    - Iterar todas las páginas y verificar que la unión de todos los `estudiantes` es igual al conjunto total; `len(union) == total`
    - **Property 6: Pagination completeness invariant**
    - **Validates: Requirements 3.10, 3.9**
  - [ ]* 4.3 Implementar Property 7 — correctitud del filtro por `activo`
    - Crear estudiantes con mezcla de `activo=True/False` vía `PUT`
    - Verificar que `?activo=true` retorna solo activos y `?activo=false` solo inactivos, y que `total` es consistente
    - **Property 7: Filter correctness**
    - **Validates: Requirements 3.6, 3.7, 3.9**

- [ ] 5. Checkpoint — pruebas properties 1–7 deben pasar
  - Ejecutar `pytest tests/test_properties.py -v --tb=short` y confirmar que todas las propiedades pasan.
  - Asegurarse de que las 39 pruebas unitarias existentes siguen pasando: `pytest tests/test_students.py -v`.
  - Preguntar al usuario si hay dudas antes de continuar.

- [ ] 6. Implementar pruebas property-based para actualización y eliminación
  - [ ] 6.1 Implementar Property 8 — invariante de actualización parcial
    - Para cualquier subconjunto no vacío de campos `F ⊂ {nombre, direccion, numero_documento, email, activo}`, verificar que solo los campos en `F` cambian y el resto se preserva exactamente
    - **Property 8: Partial update invariant**
    - **Validates: Requirements 4.1, 4.9**
  - [ ]* 6.2 Implementar Property 9 — visibilidad de eliminación
    - Después de `DELETE /students/{id}` exitoso, `GET /students/{id}` retorna 404
    - **Property 9: Deletion round-trip (visibility invariant)**
    - **Validates: Requirements 5.1, 5.6**
  - [ ]* 6.3 Implementar Property 10 — invariante de conteo de eliminación
    - Dado un conjunto de `n` estudiantes, eliminar uno y verificar que `GET /students/?total` == `n - 1`
    - **Property 10: Deletion count invariant**
    - **Validates: Requirements 5.5**

- [ ] 7. Agregar pruebas de casos borde faltantes en `test_students.py`
  - [ ] 7.1 Test de límite máximo de `direccion` (500 caracteres)
    - Añadir test: `direccion` con exactamente 500 caracteres → 201
    - Añadir test: `direccion` con 501 caracteres → 422
    - _Requirements: 1.8, 6.2_
  - [ ] 7.2 Test de `por_pagina < 1`
    - Añadir test: `GET /students/?por_pagina=0` → 422`n    - _Requirements: 3.5_
  - [ ] 7.3 Test de página más allá del total de registros
    - Añadir test: crear 2 estudiantes, `GET /students/?pagina=999&por_pagina=10` → 200, `estudiantes == []`, `total == 2`
    - _Requirements: 3.11_
  - [ ] 7.4 Test de parámetro `activo` con valor no booleano
    - Añadir test: `GET /students/?activo=maybe` → 422
    - _Requirements: 3.12_
  - [ ] 7.5 Test de headers CORS
    - Añadir test: `GET /` con header `Origin: http://example.com` → respuesta contiene `Access-Control-Allow-Origin: *`
    - Añadir test: preflight `OPTIONS /students/` con `Origin` y `Access-Control-Request-Method` → 200 con headers CORS
    - _Requirements: 10.1, 10.2_
  - [ ] 7.6 Test de errores de validación multi-campo
    - Añadir test: `POST /students/` con `nombre` vacío y `email` inválido simultáneamente → 422, la respuesta incluye errores para ambos campos
    - _Requirements: 6.5, 11.5_
  - [ ] 7.7 Test de `/health` con BD caída (mock de `verificar_conexion`)
    - Añadir test usando `unittest.mock.patch` para mockear `app.database.verificar_conexion` retornando `False`
    - Verificar que `GET /health` retorna 503 con body `{"api": "ok", "base_de_datos": "error"}`
    - _Requirements: 9.2_

- [ ] 8. Checkpoint final — suite de pruebas completa
  - Ejecutar `pytest tests/ -v --tb=short` y verificar que todas las pruebas (unitarias + property-based + nuevos casos borde) pasan.
  - Confirmar que no hay regresiones en las 39 pruebas originales.
  - Preguntar al usuario si hay dudas antes de cerrar.

---

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para una entrega MVP más rápida.
- Cada tarea referencia requisitos específicos del `requirements.md` para trazabilidad.
- Las pruebas property-based usan el fixture `client` (SQLite en memoria) para velocidad; no requieren PostgreSQL.
- Hypothesis debe configurarse en `pytest.ini` o mediante `@settings` por prueba con `max_examples=100` como mínimo.
- El archivo `tests/test_properties.py` es el destino de todas las pruebas property-based nuevas para mantenerlas separadas de los tests de ejemplo en `test_students.py`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "2.3", "3.1"] },
    { "id": 2, "tasks": ["2.2", "4.1"] },
    { "id": 3, "tasks": ["4.2", "4.3", "6.1"] },
    { "id": 4, "tasks": ["6.2", "6.3", "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7"] }
  ]
}
```

