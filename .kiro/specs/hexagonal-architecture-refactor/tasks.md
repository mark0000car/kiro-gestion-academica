# Implementation Plan: Hexagonal Architecture Refactor

## Overview

This plan migrates the flat FastAPI project to a Hexagonal (Ports & Adapters) architecture in seven sequential phases. Each phase ends with a fully green `pytest tests/ -v` run, ensuring no regressions are introduced at any point. The existing tests in `tests/test_students.py` and `tests/test_integration.py` must pass without modification throughout. New test files (`tests/test_domain.py`, `tests/test_use_cases.py`, `tests/test_properties.py`) and in-memory fakes are added alongside the implementation.

---

## Tasks

- [x] 1. Phase 1 — Domain Layer: entities, value objects, exceptions
  - [x] 1.1 Create domain exceptions module
    - Create `app/domain/__init__.py` and `app/domain/exceptions.py`
    - Implement `EntidadNoEncontrada`, `ConflictoDeUnicidad`, `ValidacionDominio` exactly as defined in the design
    - No imports from SQLAlchemy, FastAPI, or Pydantic
    - _Requirements: 2.7, 4.3, 4.4, 4.5_

  - [x] 1.2 Create `Estudiante` and `Docente` domain entities
    - Create `app/domain/entities/__init__.py`, `app/domain/entities/student.py`, `app/domain/entities/teacher.py`
    - Use `@dataclass` with fields: `nombre`, `direccion`/`especialidad`, `numero_documento`, `email`, `id: int = 0`, `activo: bool = True`, `fecha_creacion`
    - No ORM decorators or framework imports
    - _Requirements: 2.1, 2.2, 2.7_

  - [x] 1.3 Create domain value objects
    - Create `app/domain/value_objects.py` with `@dataclass(frozen=True)` classes: `Email`, `NumeroDocumento`, `Especialidad`
    - `Email.__post_init__` validates presence of `@`, non-empty prefix, and `.` in domain
    - `NumeroDocumento.__post_init__` validates pattern `^[A-Za-z0-9\-]{3,30}$`
    - `Especialidad.__post_init__` validates non-empty and `len <= 100`
    - _Requirements: 2.3, 2.4, 2.5, 2.6_

  - [ ]* 1.4 Write unit tests for domain layer (`tests/test_domain.py`)
    - Test `EntidadNoEncontrada`, `ConflictoDeUnicidad`, `ValidacionDominio` message formatting
    - Test valid construction of `Estudiante` and `Docente` dataclasses
    - Test `Email`, `NumeroDocumento`, `Especialidad` accept valid inputs
    - Test each value object rejects invalid inputs with `ValueError`
    - _Requirements: 2.4, 2.5, 2.6_

  - [ ]* 1.5 Write property tests for value objects (`tests/test_properties.py`) — Properties 1–5
    - **Property 1: Round-trip de Value Objects** — `st.emails()`, `st.from_regex(r'^[A-Za-z0-9\-]{3,30}$')`, `st.text(min_size=1, max_size=100)` → `.valor` equals input
    - **Validates: Requirements 2.3**
    - **Property 2: Email rechaza entradas inválidas** — strings without `@`, empty prefix, or domain without `.` must raise `ValueError`
    - **Validates: Requirements 2.4**
    - **Property 3: NumeroDocumento rechaza entradas inválidas** — strings outside `^[A-Za-z0-9\-]{3,30}$` must raise `ValueError`
    - **Validates: Requirements 2.5**
    - **Property 4: Especialidad rechaza entradas inválidas** — empty string or `len > 100` must raise `ValueError`
    - **Validates: Requirements 2.6**
    - **Property 5: Value Objects son inmutables** — assigning to `.valor` must raise `AttributeError`/`FrozenInstanceError`
    - **Validates: Requirements 2.3**
    - Use `@settings(max_examples=200)` on every property test
    - _Requirements: 2.3, 2.4, 2.5, 2.6_

- [x] 2. Checkpoint — Phase 1 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` and verify 0 failures before proceeding.

- [x] 3. Phase 2 — Application Ports
  - [x] 3.1 Create `EstudianteRepository` Protocol
    - Create `app/application/__init__.py`, `app/application/ports/__init__.py`
    - Create `app/application/ports/student_repository.py` with `@runtime_checkable` `EstudianteRepository(Protocol)`
    - Declare methods: `guardar`, `obtener_por_id`, `obtener_por_email`, `obtener_por_documento`, `listar`, `eliminar`
    - Use `Optional[Estudiante]`, `tuple[list[Estudiante], int]` signatures matching the design
    - No SQLAlchemy or FastAPI imports; only domain imports
    - Docstring each method with parameters, return type, and exceptions
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.6_

  - [x] 3.2 Create `DocenteRepository` Protocol
    - Create `app/application/ports/teacher_repository.py` with `@runtime_checkable` `DocenteRepository(Protocol)`
    - Declare methods: `guardar`, `obtener_por_id`, `obtener_por_email`, `obtener_por_especialidad`, `listar`, `eliminar`
    - No SQLAlchemy or FastAPI imports; only domain imports
    - Docstring each method with parameters, return type, and exceptions
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 4. Checkpoint — Phase 2 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — existing tests must still report 0 failures.

- [x] 5. Phase 3 — Use Cases + In-Memory Repositories
  - [x] 5.1 Create in-memory repository fakes
    - Create `tests/fakes/__init__.py`
    - Create `tests/fakes/in_memory_student_repository.py` with `InMemoryEstudianteRepository`
    - Implement all six `EstudianteRepository` methods; assign auto-incremented `id` on first `guardar` (`id == 0`); enforce uniqueness on `email` and `numero_documento`, raising `ConflictoDeUnicidad`
    - Create `tests/fakes/in_memory_teacher_repository.py` with `InMemoryDocenteRepository` analogously (unique on `email` and `especialidad`)
    - _Requirements: 4.9, 7.3_

  - [x] 5.2 Implement student use cases
    - Create `app/application/use_cases/__init__.py`, `app/application/use_cases/student/__init__.py`
    - Implement `CrearEstudiante`, `ObtenerEstudiante`, `ListarEstudiantes`, `ActualizarEstudiante`, `EliminarEstudiante`
    - Each class receives its repository via `__init__`; exposes a single `ejecutar(...)` method
    - `CrearEstudiante.ejecutar`: check email and documento uniqueness via port, raise `ConflictoDeUnicidad`; then `repo.guardar`
    - `ObtenerEstudiante.ejecutar`: raise `EntidadNoEncontrada` if `obtener_por_id` returns `None`
    - `ActualizarEstudiante.ejecutar`: raise `EntidadNoEncontrada` if not found; no-op (return entity unchanged) when `**campos` is empty
    - `EliminarEstudiante.ejecutar`: raise `EntidadNoEncontrada` if `eliminar` returns `False`
    - No SQLAlchemy or FastAPI imports
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

  - [x] 5.3 Implement teacher use cases
    - Create `app/application/use_cases/teacher/__init__.py`
    - Implement `CrearDocente`, `ObtenerDocente`, `ListarDocentes`, `ActualizarDocente`, `EliminarDocente`
    - Mirror the student use case structure, using `DocenteRepository` and `Docente` entity
    - `CrearDocente.ejecutar`: check uniqueness on `email` and `especialidad`
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

  - [ ]* 5.4 Write unit tests for use cases (`tests/test_use_cases.py`)
    - Use `InMemoryEstudianteRepository` and `InMemoryDocenteRepository` — no DB, no HTTP
    - Test `CrearEstudiante`: success, duplicate email raises `ConflictoDeUnicidad`, duplicate documento raises `ConflictoDeUnicidad`
    - Test `ObtenerEstudiante`: found returns entity; unknown ID raises `EntidadNoEncontrada`
    - Test `ListarEstudiantes`: empty repo, single page, multi-page, `solo_activos` filter
    - Test `ActualizarEstudiante`: field update, no-op on empty dict, unknown ID raises `EntidadNoEncontrada`, duplicate email raises `ConflictoDeUnicidad`
    - Test `EliminarEstudiante`: success, unknown ID raises `EntidadNoEncontrada`
    - Mirror all above for docente use cases
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.7, 4.8_

  - [ ]* 5.5 Write property tests for use cases (`tests/test_properties.py`) — Properties 6–11
    - **Property 6: Repositorio en memoria devuelve None para IDs desconocidos** — any positive int not stored returns `None` from all three lookup methods
    - **Validates: Requirements 3.6**
    - **Property 7: Casos de Uso lanzan EntidadNoEncontrada para entidades inexistentes** — empty repo + any positive int → `ObtenerEstudiante`, `ActualizarEstudiante`, `EliminarEstudiante` raise `EntidadNoEncontrada`; repo size unchanged
    - **Validates: Requirements 4.4, 4.8**
    - **Property 8: Casos de Uso lanzan ConflictoDeUnicidad para campos únicos duplicados** — after storing student, calling `CrearEstudiante` with same `email` or `numero_documento` raises `ConflictoDeUnicidad`; repo size unchanged
    - **Validates: Requirements 4.5**
    - **Property 9: Actualizar sin campos es una operación sin efecto** — stored student + empty `**campos` → returned entity equals original; no write calls issued
    - **Validates: Requirements 4.7**
    - **Property 10: Invariante de paginación** — any `n` students, any valid `por_pagina` in [1,100] → `len(result) <= por_pagina` and `total == n`
    - **Validates: Requirements 6.8**
    - **Property 11: Entradas inválidas al Caso de Uso no mutan el repositorio** — invalid input (empty name, bad email) raises a non-`HTTPException` exception; repo size before equals repo size after
    - **Validates: Requirements 4.3, 6.6**
    - Use `@settings(max_examples=200)` on every property test
    - _Requirements: 3.6, 4.3, 4.4, 4.5, 4.7, 4.8, 6.6, 6.8_

- [-] 6. Checkpoint — Phase 3 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — existing tests must still report 0 failures; new domain and use-case tests must all pass.

- [ ] 7. Phase 4 — SQLAlchemy Persistence Adapters
  - [~] 7.1 Create infrastructure config modules
    - Create `app/infrastructure/__init__.py`, `app/infrastructure/config/__init__.py`
    - Create `app/infrastructure/config/settings.py` — migrate `Settings` class from `app/config.py`; keep `settings` singleton
    - Create `app/infrastructure/config/database.py` — migrate `engine`, `SessionLocal`, `Base`, `get_db`, `verificar_conexion` from `app/database.py`
    - Keep `app/config.py` and `app/database.py` intact (they re-export from new paths) so existing imports don't break yet
    - _Requirements: 1.4, 1.7, 7.4_

  - [~] 7.2 Create ORM models
    - Create `app/infrastructure/persistence/__init__.py`
    - Create `app/infrastructure/persistence/models.py` with `EstudianteORM` and `DocenteORM` using `app.infrastructure.config.database.Base`
    - Column definitions must exactly match the current `app/models.py` schema (same column names, types, constraints, `__tablename__`)
    - Do not emit any DDL statements
    - _Requirements: 5.1, 5.6_

  - [~] 7.3 Implement `SQLAlchemyEstudianteRepository`
    - Create `app/infrastructure/persistence/student_repository.py`
    - Implement all six `EstudianteRepository` methods
    - `_a_dominio(orm)` converts `EstudianteORM` → `Estudiante` domain entity
    - `_a_orm(entidad)` converts `Estudiante` → `EstudianteORM`
    - `guardar`: detect insert vs update via `entidad.id == 0`; catch `IntegrityError`, rollback, inspect message, raise `ConflictoDeUnicidad("email")` or `ConflictoDeUnicidad("numero_documento")`
    - `listar`: accepts `pagina`, `por_pagina`, `solo_activos`; mirrors `crud.listar_estudiantes` behavior
    - `eliminar`: returns `True` if found and deleted, `False` otherwise
    - _Requirements: 5.2, 5.4, 5.7_

  - [~] 7.4 Implement `SQLAlchemyDocenteRepository`
    - Create `app/infrastructure/persistence/teacher_repository.py`
    - Implement all six `DocenteRepository` methods mirroring the student repository pattern
    - `guardar`: catch `IntegrityError` for `email` and `especialidad` uniqueness violations
    - _Requirements: 5.3, 5.5, 5.7_

- [~] 8. Checkpoint — Phase 4 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — 0 failures; SQLAlchemy repos exist but are not yet wired to routers.

- [ ] 9. Phase 5 — FastAPI HTTP Adapters (routers + schemas)
  - [~] 9.1 Create Pydantic HTTP schemas
    - Create `app/infrastructure/http/__init__.py`, `app/infrastructure/http/schemas/__init__.py`
    - Create `app/infrastructure/http/schemas/student.py` — migrate `EstudianteCreate`, `EstudianteUpdate`, `EstudianteResponse`, `EstudiantePaginado` from `app/schemas.py`; keep all validators and `model_config` unchanged
    - Create `app/infrastructure/http/schemas/teacher.py` — migrate `DocenteCreate`, `DocenteUpdate`, `DocenteResponse`, `DocentePaginado`
    - _Requirements: 6.3, 6.7_

  - [~] 9.2 Create HTTP dependencies module
    - Create `app/infrastructure/http/dependencies.py`
    - Implement `get_estudiante_repo(db: Session = Depends(get_db)) -> SQLAlchemyEstudianteRepository`
    - Implement `get_docente_repo(db: Session = Depends(get_db)) -> SQLAlchemyDocenteRepository`
    - Import `get_db` from `app.infrastructure.config.database`
    - _Requirements: 7.1, 7.2_

  - [~] 9.3 Implement students HTTP router
    - Create `app/infrastructure/http/routers/__init__.py`
    - Create `app/infrastructure/http/routers/students.py`
    - Implement 5 endpoints: `POST /students/`, `GET /students/`, `GET /students/{id}`, `PUT /students/{id}`, `DELETE /students/{id}`
    - Each endpoint resolves repo via `Depends(get_estudiante_repo)`, constructs the use case, calls `ejecutar`
    - Translate exceptions: `EntidadNoEncontrada` → 404, `ConflictoDeUnicidad` → 409, `ValidacionDominio` → 422
    - Helper `_a_response(entidad)` converts domain entity to `EstudianteResponse`
    - Preserve all path, method, query param, status code, and response schema contracts from the existing router
    - _Requirements: 6.1, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [~] 9.4 Implement teachers HTTP router
    - Create `app/infrastructure/http/routers/teachers.py`
    - Implement 5 endpoints: `POST /teachers/`, `GET /teachers/`, `GET /teachers/{id}`, `PUT /teachers/{id}`, `DELETE /teachers/{id}`
    - Mirror the students router pattern using teacher use cases and `get_docente_repo`
    - Translate same domain exceptions to same HTTP codes
    - _Requirements: 6.2, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

- [~] 10. Checkpoint — Phase 5 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — 0 failures; new routers exist but `app/main.py` still points to old routers.

- [ ] 11. Phase 6 — Dependency Injection Wiring, main.py, conftest.py
  - [~] 11.1 Update `app/main.py`
    - Replace imports of `app.routers.students` and `app.routers.teachers` with `app.infrastructure.http.routers.students` and `app.infrastructure.http.routers.teachers`
    - Replace import of `app.database.verificar_conexion` with `app.infrastructure.config.database.verificar_conexion`
    - `main.py` must contain only: FastAPI instantiation, router registration, CORS middleware, lifespan, and root/health endpoints
    - _Requirements: 1.6, 1.7, 6.7_

  - [~] 11.2 Update `tests/conftest.py`
    - Update `from app.database import Base, get_db` → `from app.infrastructure.config.database import Base, get_db`
    - Update `from app.models import Docente, Estudiante` (PostgreSQL teardown) → `from app.infrastructure.persistence.models import DocenteORM as Docente, EstudianteORM as Estudiante`
    - Update `from app.config import settings` → `from app.infrastructure.config.settings import settings`
    - All other logic (`dependency_overrides`, SQLite engine, PostgreSQL engine) remains unchanged
    - _Requirements: 7.3, 7.5, 8.1, 8.5, 8.6_

- [~] 12. Checkpoint — Phase 6 complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — all tests including integration tests must report 0 failures.

- [ ] 13. Phase 7 — Cleanup: Remove Legacy Flat Modules
  - [~] 13.1 Verify all public symbols are accessible from new paths
    - Confirm `app.infrastructure.http.schemas.student` exports all `EstudianteCreate`, `EstudianteUpdate`, `EstudianteResponse`, `EstudiantePaginado`
    - Confirm `app.infrastructure.http.schemas.teacher` exports all `DocenteCreate`, `DocenteUpdate`, `DocenteResponse`, `DocentePaginado`
    - Confirm `app.infrastructure.persistence.models` exports `EstudianteORM`, `DocenteORM`
    - Confirm `app.infrastructure.config.settings` exports `settings`
    - Confirm `app.infrastructure.config.database` exports `Base`, `get_db`, `verificar_conexion`, `engine`, `SessionLocal`
    - Run `pytest tests/ -v` — must report 0 failures before proceeding to deletion
    - _Requirements: 1.5, 1.7_

  - [~] 13.2 Delete legacy flat modules
    - Delete `app/crud.py`
    - Delete `app/models.py`
    - Delete `app/schemas.py`
    - Delete `app/config.py`
    - Delete `app/database.py`
    - Delete `app/routers/students.py`, `app/routers/teachers.py`, and `app/routers/__init__.py` (if the `routers/` directory is now empty)
    - _Requirements: 1.1, 1.5_

  - [ ]* 13.3 Write final integration smoke tests
    - Add assertions in `tests/test_use_cases.py` or a new `tests/test_smoke.py` confirming no module in `app/domain/` or `app/application/` imports from `sqlalchemy`, `fastapi`, or `pydantic`
    - Use `ast` or `importlib` to inspect import statements statically
    - _Requirements: 2.7, 4.6, 1.2, 1.3_

- [~] 14. Final Checkpoint — Migration complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run `pytest tests/ -v` — 0 failures, 0 errors, 0 unexpected skips.
  - Confirm directory structure matches the design: `app/domain/`, `app/application/`, `app/infrastructure/`; no legacy files under `app/` root.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster migration, but are strongly recommended for catching regressions early.
- Each numbered checkpoint task is a hard gate: do not advance to the next phase if `pytest` reports any failure.
- All property tests use `@settings(max_examples=200)` and carry a docstring tag in the format `Feature: hexagonal-architecture-refactor, Property N: <title>`.
- The `conftest.py` `dependency_overrides[get_db]` mechanism is preserved unchanged; the only updates are the two import paths.
- `app/config.py` and `app/database.py` may optionally be kept as thin re-export shims during phases 4–6 to avoid breaking intermediate states, then deleted in phase 7.
- The ORM models are renamed (`EstudianteORM`, `DocenteORM`) in the persistence layer to avoid name collision with the domain entities (`Estudiante`, `Docente`).

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["1.4", "1.5"] },
    { "id": 2, "tasks": ["3.1", "3.2"] },
    { "id": 3, "tasks": ["5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3"] },
    { "id": 5, "tasks": ["5.4", "5.5"] },
    { "id": 6, "tasks": ["7.1"] },
    { "id": 7, "tasks": ["7.2"] },
    { "id": 8, "tasks": ["7.3", "7.4"] },
    { "id": 9, "tasks": ["9.1", "9.2"] },
    { "id": 10, "tasks": ["9.3", "9.4"] },
    { "id": 11, "tasks": ["11.1"] },
    { "id": 12, "tasks": ["11.2"] },
    { "id": 13, "tasks": ["13.1"] },
    { "id": 14, "tasks": ["13.2"] },
    { "id": 15, "tasks": ["13.3"] }
  ]
}
```
