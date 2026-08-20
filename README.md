# Sistema de Gestión de Estudiantes

API RESTful construida con **FastAPI** y **PostgreSQL** para el registro y administración de estudiantes.

---

## Estructura del proyecto

```
gestion-academica/
├── app/
│   ├── __init__.py
│   ├── main.py          # Punto de entrada FastAPI
│   ├── config.py        # Variables de entorno (pydantic-settings)
│   ├── database.py      # Motor SQLAlchemy + pool de conexiones
│   ├── models.py        # Modelo ORM Estudiante
│   ├── schemas.py       # Esquemas Pydantic (validación)
│   ├── crud.py          # Capa de acceso a datos
│   └── routers/
│       └── students.py  # Endpoints CRUD /students
├── migrations/
│   └── create_students_table.sql
├── tests/
│   ├── conftest.py          # Fixtures (SQLite en memoria + PostgreSQL)
│   ├── test_students.py     # Pruebas unitarias (sin BD real)
│   └── test_integration.py  # Pruebas de integración (PostgreSQL real)
├── .env
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Requisitos previos

- Python 3.9 o superior
- PostgreSQL instalado y corriendo
- `pip` para instalar dependencias

---

## Instalación y ejecución paso a paso

### 1. Clonar o descargar el proyecto

```bash
cd gestion-academica
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
DB_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/gac
API_PORT=8000
```

### 5. Crear la base de datos en PostgreSQL

```sql
-- Conectarse a PostgreSQL como superusuario y ejecutar:
CREATE DATABASE gac;
```

### 6. Ejecutar la migración

```bash
# Opción A: usando psql
psql -U postgres -d gac -f migrations/create_students_table.sql

# Opción B: dejar que SQLAlchemy cree la tabla automáticamente
# (se hace al iniciar la aplicación si se descomenta en main.py)
```

> **Nota:** La API crea la tabla automáticamente al iniciar si usas el comando de abajo y la tabla no existe. El script SQL es la forma recomendada en producción.

### 7. Iniciar la API

```bash
uvicorn app.main:app --reload --port 8000
```

La API quedará disponible en:

| Recurso | URL |
|---------|-----|
| API base | http://localhost:8000 |
| Documentación Swagger | http://localhost:8000/docs |
| Documentación ReDoc | http://localhost:8000/redoc |
| Estado del servicio | http://localhost:8000/health |

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/students/` | Crear un nuevo estudiante |
| `GET` | `/students/` | Listar todos (paginado) |
| `GET` | `/students/{id}` | Obtener por ID |
| `PUT` | `/students/{id}` | Actualizar datos |
| `DELETE` | `/students/{id}` | Eliminar estudiante |
| `GET` | `/health` | Estado de la API y BD |

### Parámetros de paginación (`GET /students/`)

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `pagina` | int | 1 | Número de página (≥ 1) |
| `por_pagina` | int | 10 | Registros por página (1-100) |
| `activo` | bool | null | Filtrar por estado |

### Códigos HTTP utilizados

| Código | Significado |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 400 | Solicitud inválida (cuerpo vacío en PUT) |
| 404 | Estudiante no encontrado |
| 409 | Conflicto (email o documento duplicado) |
| 422 | Error de validación Pydantic |
| 500 | Error interno del servidor |
| 503 | Base de datos no disponible |

---

## Modelo de datos

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

### Validaciones aplicadas

- `nombre`: requerido, máx. 200 caracteres, no puede estar vacío.
- `direccion`: requerido, no puede estar vacía.
- `numero_documento`: requerido, solo letras, números y guiones, 3-30 caracteres, único.
- `email`: formato de email válido, único en el sistema.

---

## Ejemplos de uso con curl

```bash
# Crear estudiante
curl -X POST http://localhost:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana García","direccion":"Calle 10","numero_documento":"1020304050","email":"ana@ejemplo.com"}'

# Obtener por ID
curl http://localhost:8000/students/1

# Listar (página 1, 5 por página)
curl "http://localhost:8000/students/?pagina=1&por_pagina=5"

# Actualizar
curl -X PUT http://localhost:8000/students/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana López","activo":false}'

# Eliminar
curl -X DELETE http://localhost:8000/students/1
```

---

## Pruebas

### Ejecutar todas las pruebas (unitarias, sin PostgreSQL)

```bash
pytest tests/test_students.py -v
```

### Ejecutar pruebas de integración (requiere PostgreSQL)

```bash
pytest tests/test_integration.py -v
```

### Ejecutar todas las pruebas

```bash
pytest -v
```

### Ejecutar con reporte de cobertura

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

Las pruebas de integración se saltan automáticamente si PostgreSQL no está disponible.

---

## Variables de entorno — referencia completa

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
# kiro-gestion-academica
