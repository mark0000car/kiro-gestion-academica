# Sistema de Gestión Académica

API RESTful construida con **FastAPI** y **PostgreSQL** para el registro y administración de estudiantes y docentes, siguiendo una arquitectura hexagonal (Ports & Adapters).

---

## Estructura del proyecto

```
kiro-gestion-academica/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Variables de entorno (pydantic-settings)
│   ├── database.py          # Motor SQLAlchemy + pool de conexiones
│   ├── models.py            # Modelos ORM (Estudiante, Docente)
│   ├── schemas.py           # Esquemas Pydantic (validación E/S)
│   ├── crud.py              # Capa de acceso a datos
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── student.py   # Entidad de dominio Estudiante
│   │   │   └── teacher.py   # Entidad de dominio Docente
│   │   ├── exceptions.py    # Excepciones de dominio
│   │   └── value_objects.py # Objetos de valor
│   ├── application/
│   │   ├── ports/
│   │   │   ├── student_repository.py  # Puerto del repositorio de estudiantes
│   │   │   └── teacher_repository.py  # Puerto del repositorio de docentes
│   │   └── use_cases/
│   │       ├── student/
│   │       │   ├── crear_estudiante.py
│   │       │   ├── obtener_estudiante.py
│   │       │   ├── listar_estudiantes.py
│   │       │   ├── actualizar_estudiante.py
│   │       │   └── eliminar_estudiante.py
│   │       └── teacher/
│   │           ├── crear_docente.py
│   │           ├── obtener_docente.py
│   │           ├── listar_docentes.py
│   │           ├── actualizar_docente.py
│   │           └── eliminar_docente.py
│   └── routers/
│       ├── students.py      # Endpoints CRUD /students
│       └── teachers.py      # Endpoints CRUD /teachers
├── migrations/
│   └── create_students_table.sql
├── tests/
│   ├── conftest.py          # Fixtures (SQLite en memoria + PostgreSQL)
│   ├── fakes/
│   │   ├── in_memory_student_repository.py
│   │   └── in_memory_teacher_repository.py
│   ├── test_students.py     # Pruebas unitarias de estudiantes
│   ├── test_teachers.py     # Pruebas unitarias de docentes
│   └── test_integration.py  # Pruebas de integración (PostgreSQL real)
├── .env
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Arquitectura

El proyecto implementa **Arquitectura Hexagonal (Ports & Adapters)**:

| Capa | Responsabilidad |
|------|----------------|
| **Domain** | Entidades de negocio (`Estudiante`, `Docente`) y excepciones de dominio |
| **Application** | Casos de uso e interfaces de repositorio (puertos) |
| **Infrastructure** | Adaptadores: ORM SQLAlchemy, routers FastAPI, esquemas Pydantic |

---

## Requisitos previos

- Python 3.9 o superior
- PostgreSQL instalado y corriendo
- `pip` para instalar dependencias

---

## Instalación y ejecución

### 1. Clonar o descargar el proyecto

```bash
cd kiro-gestion-academica
```

### 2. Crear y activar un entorno virtual

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Edita el archivo `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gac
DB_USER=postgres
DB_PASSWORD=XXXXXX
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gac
API_PORT=8000
```

### 5. Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE gac;
```

### 6. Ejecutar la migración

```bash
# Opción A: usando psql
psql -U postgres -d gac -f migrations/create_students_table.sql

# Opción B: dejar que SQLAlchemy cree las tablas automáticamente al iniciar
```

### 7. Iniciar la API

```bash
uvicorn app.main:app --reload --port 8000
```

| Recurso | URL |
|---------|-----|
| API base | http://localhost:8000 |
| Documentación Swagger | http://localhost:8000/docs |
| Documentación ReDoc | http://localhost:8000/redoc |
| Estado del servicio | http://localhost:8000/health |

---

## Endpoints disponibles

### Estudiantes

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/students/` | Crear un nuevo estudiante |
| `GET` | `/students/` | Listar todos (paginado) |
| `GET` | `/students/{id}` | Obtener por ID |
| `PUT` | `/students/{id}` | Actualizar datos |
| `DELETE` | `/students/{id}` | Eliminar estudiante |

### Docentes

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/teachers/` | Crear un nuevo docente |
| `GET` | `/teachers/` | Listar todos (paginado) |
| `GET` | `/teachers/{id}` | Obtener por ID |
| `PUT` | `/teachers/{id}` | Actualizar datos |
| `DELETE` | `/teachers/{id}` | Eliminar docente |

### Utilidades

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Bienvenida y links de documentación |
| `GET` | `/health` | Estado de la API y la base de datos |

---

## Parámetros de paginación

Aplica a `GET /students/` y `GET /teachers/`:

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `pagina` | int | 1 | Número de página (≥ 1) |
| `por_pagina` | int | 10 | Registros por página (1-100) |
| `activo` | bool | null | Filtrar por estado activo/inactivo |

---

## Códigos HTTP utilizados

| Código | Significado |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 404 | Recurso no encontrado |
| 409 | Conflicto (email o documento duplicado) |
| 422 | Error de validación Pydantic |
| 500 | Error interno del servidor |
| 503 | Base de datos no disponible |

---

## Modelos de datos

### Estudiante

```json
{
  "id": 1,
  "nombre": "Ana García",
  "direccion": "Calle 10 # 20-30, Bogotá",
  "numero_documento": "1020304050",
  "email": "ana.garcia@ejemplo.com",
  "activo": true,
  "fecha_creacion": "2024-01-15T10:30:00Z"
}
```

**Validaciones:**
- `nombre`: requerido, máx. 200 caracteres.
- `direccion`: requerido, no puede estar vacía.
- `numero_documento`: solo letras, números y guiones (3-30 caracteres), único.
- `email`: formato válido, único en el sistema.

### Docente

```json
{
  "id": 1,
  "nombre": "Carlos Martínez",
  "email": "carlos.martinez@ejemplo.com",
  "especialidad": "Matemáticas",
  "activo": true,
  "fecha_creacion": "2024-01-15T10:30:00Z"
}
```

**Validaciones:**
- `nombre`: requerido, máx. 200 caracteres.
- `email`: formato válido, único en el sistema.
- `especialidad`: requerido, máx. 200 caracteres, único en el sistema.

---

## Ejemplos de uso con curl

### Estudiantes

```bash
# Crear estudiante
curl -X POST http://localhost:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana García","direccion":"Calle 10","numero_documento":"1020304050","email":"ana@ejemplo.com"}'

# Listar (página 1, 5 por página)
curl "http://localhost:8000/students/?pagina=1&por_pagina=5"

# Obtener por ID
curl http://localhost:8000/students/1

# Actualizar
curl -X PUT http://localhost:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana López","activo":false}'

# Eliminar
curl -X DELETE http://localhost:8000/students/1
```

### Docentes

```bash
# Crear docente
curl -X POST http://localhost:8000/teachers/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Carlos Martínez","email":"carlos@ejemplo.com","especialidad":"Matemáticas"}'

# Listar (página 1, 10 por página, solo activos)
curl "http://localhost:8000/teachers/?pagina=1&por_pagina=10&activo=true"

# Obtener por ID
curl http://localhost:8000/teachers/1

# Actualizar
curl -X PUT http://localhost:8000/teachers/1 \
  -H "Content-Type: application/json" \
  -d '{"especialidad":"Física","activo":false}'

# Eliminar
curl -X DELETE http://localhost:8000/teachers/1
```

---

## Pruebas

### Archivos de prueba

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `tests/test_students.py` | Unitaria | 39 pruebas para endpoints `/students/` — usa SQLite en memoria |
| `tests/test_teachers.py` | Unitaria | 39 pruebas para endpoints `/teachers/` — usa SQLite en memoria |
| `tests/test_integration.py` | Integración | 19 pruebas sobre PostgreSQL real (estudiantes + docentes) |

### Cobertura de pruebas unitarias

**Estudiantes y Docentes** siguen la misma estructura de 5 grupos:

| Grupo | Tests | Escenarios cubiertos |
|-------|-------|----------------------|
| `TestCrear*` | 10 | Creación exitosa, duplicados (email/documento o especialidad), email inválido, campos faltantes/vacíos, campos en respuesta |
| `TestObtener*` | 4 | Por ID existente, 404, ID no numérico, datos completos |
| `TestListar*` | 8 | Lista vacía, con datos, paginación, 2ª página, filtro `activo`, límite 100, página 0, estructura de respuesta |
| `TestActualizar*` | 12 | Cada campo por separado, múltiples campos, no existente, conflictos de unicidad, body vacío (no-op), validaciones, preservación de campos |
| `TestEliminar*` | 5 | Exitoso, 404 post-delete, no existente, reducción de total, ID inválido |

### Cobertura de pruebas de integración

| Test | Descripción |
|------|-------------|
| `test_conexion_postgresql` | Conexión real a PostgreSQL |
| `test_tabla_estudiantes_existe` | Existencia de tabla `estudiantes` |
| `test_tabla_docentes_existe` | Existencia de tabla `docentes` |
| `test_pg_crear_y_obtener_estudiante` | CRUD completo estudiante |
| `test_pg_email_duplicado_estudiante` | Conflicto 409 en email |
| `test_pg_documento_duplicado` | Conflicto 409 en documento |
| `test_pg_listar_estudiantes_paginado` | Paginación real |
| `test_pg_actualizar_estudiante` | Actualización parcial |
| `test_pg_eliminar_estudiante` | Eliminación y 404 posterior |
| `test_pg_actualizacion_parcial_no_modifica_otros_campos_estudiante` | Preservación de campos |
| `test_pg_crear_y_obtener_docente` | CRUD completo docente |
| `test_pg_email_duplicado_docente` | Conflicto 409 en email de docente |
| `test_pg_especialidad_duplicada` | Conflicto 409 en especialidad |
| `test_pg_listar_docentes_paginado` | Paginación real de docentes |
| `test_pg_actualizar_docente` | Actualización de nombre |
| `test_pg_actualizar_especialidad_docente` | Actualización de especialidad |
| `test_pg_eliminar_docente` | Eliminación y 404 posterior |
| `test_pg_actualizacion_parcial_no_modifica_otros_campos_docente` | Preservación de campos |
| `test_pg_docente_cuerpo_vacio_no_modifica` | Body vacío es no-op |
| `test_pg_health_check_con_bd_real` | Health check con BD real |

### Comandos

```bash
# Pruebas unitarias de estudiantes (sin PostgreSQL)
pytest tests/test_students.py -v

# Pruebas unitarias de docentes (sin PostgreSQL)
pytest tests/test_teachers.py -v

# Todas las pruebas unitarias
pytest tests/test_students.py tests/test_teachers.py -v

# Pruebas de integración (requiere PostgreSQL)
pytest tests/test_integration.py -v

# Todas las pruebas
pytest -v

# Con reporte de cobertura
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

Las pruebas de integración se saltan automáticamente si PostgreSQL no está disponible.

---

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la base de datos | `gac` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `postgres` |
| `DATABASE_URL` | URL completa de conexión | `postgresql://postgres:postgres@localhost:5432/gac` |
| `API_PORT` | Puerto donde corre la API | `8000` |

---

## Tecnologías utilizadas

| Componente | Tecnología |
|------------|------------|
| Framework API | FastAPI 0.111 |
| Servidor ASGI | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Driver PostgreSQL | psycopg2-binary |
| Validación | Pydantic v2 |
| Configuración | pydantic-settings |
| Pruebas | pytest + httpx |
| BD pruebas unitarias | SQLite en memoria |
