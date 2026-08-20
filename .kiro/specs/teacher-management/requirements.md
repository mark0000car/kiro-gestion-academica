# Requirements Document

## Introduction

Este documento describe los requisitos funcionales y no funcionales para el módulo de **Gestión de Docentes** del Sistema de Gestión Académica. El módulo expone una API RESTful que permite registrar, consultar, actualizar y eliminar docentes, siguiendo los mismos patrones arquitectónicos del módulo de estudiantes ya existente (FastAPI + SQLAlchemy + PostgreSQL).

El módulo incluye:
- Cinco endpoints CRUD sobre `/teachers`.
- Validación de datos de entrada con Pydantic v2.
- Pool de conexiones a PostgreSQL configurable por variables de entorno.
- Script de migración para crear la tabla de docentes.
- Suite de pruebas unitarias con pytest y httpx.
- Actualización del README con documentación del nuevo módulo.

---

## Glossary

- **API**: Interfaz de programación de aplicaciones que expone los endpoints HTTP del sistema.
- **Docente**: Entidad que representa a un profesor registrado en el sistema, con campos `id`, `nombre`, `email`, `especialidad`, `fecha_creacion` y `activo`.
- **CRUD**: Conjunto de operaciones Crear, Leer, Actualizar y Eliminar sobre un recurso.
- **Pool_de_Conexiones**: Conjunto reutilizable de conexiones a PostgreSQL gestionado por SQLAlchemy `QueuePool`.
- **Pydantic_Validator**: Componente de validación de datos de entrada y salida basado en Pydantic v2.
- **CRUD_Layer**: Módulo `crud.py` que encapsula todas las operaciones de acceso a la base de datos.
- **Router**: Módulo `routers/teachers.py` que define los endpoints HTTP y delega la lógica al `CRUD_Layer`.
- **Migration_Script**: Archivo `migrations/create_teachers_table.sql` que define el DDL para crear la tabla `docentes`.
- **Init_Script**: Archivo `init_db.py` que ejecuta la migración programáticamente al iniciar o bajo demanda.
- **Test_Suite**: Conjunto de pruebas unitarias en `tests/test_teachers.py` que usan SQLite en memoria.
- **Integration_Test_Suite**: Conjunto de pruebas de integración en `tests/test_teachers_integration.py` que usan PostgreSQL real.
- **ORM**: Mapeador objeto-relacional; en este proyecto SQLAlchemy 2.0.
- **HTTP_409**: Código de respuesta que indica conflicto de unicidad (email o especialidad duplicados).
- **HTTP_422**: Código de respuesta que indica error de validación de datos de entrada.

---

## Requirements

### Requisito 1: Creación de un docente

**User Story:** Como administrador del sistema, quiero crear un nuevo docente, para que quede registrado en el sistema con sus datos básicos.

#### Criterios de Aceptación

1. WHEN el cliente envía una solicitud `POST /teachers` con `nombre`, `email` y `especialidad` válidos, THE API SHALL persistir el docente en la base de datos y devolver la representación completa del recurso creado con código HTTP 201.
2. WHEN el cliente envía una solicitud `POST /teachers` con campos válidos, THE API SHALL asignar automáticamente un `id` entero autoincremental único, una `fecha_creacion` con la marca de tiempo UTC del servidor y el valor `activo = true`.
3. IF el `email` enviado ya existe en la tabla `docentes`, THEN THE API SHALL devolver HTTP 409 con un mensaje que identifique el campo en conflicto sin persistir ningún dato.
4. IF la `especialidad` enviada ya existe en la tabla `docentes`, THEN THE API SHALL devolver HTTP 409 con un mensaje que identifique el campo en conflicto sin persistir ningún dato.
5. IF alguno de los campos requeridos (`nombre`, `email`, `especialidad`) está ausente o su valor es una cadena vacía o contiene únicamente espacios en blanco, THEN THE API SHALL devolver HTTP 422 con un mensaje que identifique cada campo inválido sin persistir ningún dato.
6. IF el valor del campo `email` no tiene formato de correo electrónico válido según RFC 5322, THEN THE API SHALL devolver HTTP 422 con un mensaje que indique el campo y el motivo del rechazo sin persistir ningún dato.
7. IF el valor del campo `nombre` supera los 200 caracteres, THEN THE API SHALL devolver HTTP 422 con un mensaje que indique el campo y el límite excedido sin persistir ningún dato.
8. IF el valor del campo `especialidad` supera los 200 caracteres, THEN THE API SHALL devolver HTTP 422 con un mensaje que indique el campo y el límite excedido sin persistir ningún dato.
9. IF la base de datos no está disponible al momento de procesar la solicitud `POST /teachers`, THEN THE API SHALL devolver HTTP 503 con un mensaje que indique que el servicio no está disponible sin persistir ningún dato parcial.

---

### Requisito 2: Consulta de un docente por ID

**User Story:** Como administrador del sistema, quiero obtener los datos de un docente por su identificador, para visualizar su información completa.

#### Criterios de Aceptación

1. WHEN el cliente envía una solicitud `GET /teachers/{id}` con un `id` entero positivo que existe en la base de datos, THE API SHALL devolver la representación completa del docente con código HTTP 200, incluyendo los campos `id`, `nombre`, `email`, `especialidad`, `fecha_creacion` y `activo`.
2. IF el `id` indicado no corresponde a ningún docente registrado, THEN THE API SHALL devolver HTTP 404 con un cuerpo JSON que contenga un mensaje descriptivo indicando que el docente con ese `id` no existe.
3. IF el `id` proporcionado no es un entero válido, THEN THE API SHALL devolver HTTP 422 con un mensaje que indique el campo inválido y la razón del rechazo.
4. WHEN el docente solicitado tiene `activo = false`, THE API SHALL devolver la representación completa del docente con código HTTP 200 sin tratarlo como un recurso no encontrado.

---

### Requisito 3: Listado paginado de docentes

**User Story:** Como administrador del sistema, quiero listar todos los docentes con soporte de paginación y filtrado por estado, para navegar el registro completo de forma eficiente.

#### Criterios de Aceptación

1. WHEN el cliente envía una solicitud `GET /teachers`, THE API SHALL devolver HTTP 200 con un objeto que contiene `total`, `pagina`, `por_pagina` y la lista `docentes`.
2. WHEN el parámetro `pagina` no se proporciona, THE API SHALL usar el valor predeterminado `1`.
3. WHEN el parámetro `por_pagina` no se proporciona, THE API SHALL usar el valor predeterminado `10`.
4. IF el parámetro `por_pagina` es mayor a 100, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el límite máximo permitido.
5. IF el parámetro `pagina` es menor a 1, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el valor mínimo permitido.
6. IF el parámetro `por_pagina` es menor a 1, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el valor mínimo permitido.
7. WHERE el parámetro `activo` se proporciona con valor booleano válido, THE CRUD_Layer SHALL filtrar los docentes devueltos según el valor booleano indicado.
8. IF el parámetro `activo` se proporciona con un valor que no sea booleano, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el campo y el tipo esperado.
9. WHEN la base de datos no contiene docentes o ningún docente coincide con los filtros aplicados, THE API SHALL devolver `total = 0` y `docentes = []` con código HTTP 200.
10. THE API SHALL ordenar los docentes devueltos por `id` ascendente para garantizar paginación determinista.

---

### Requisito 4: Actualización de un docente

**User Story:** Como administrador del sistema, quiero actualizar los datos de un docente existente, para corregir o modificar su información.

#### Criterios de Aceptación

1. WHEN el cliente envía una solicitud `PUT /teachers/{id}` con al menos un campo válido, THE CRUD_Layer SHALL aplicar únicamente los campos presentes en el cuerpo y THE API SHALL devolver la representación completa del docente actualizado con HTTP 200.
2. IF el `id` indicado no corresponde a ningún docente registrado, THEN THE API SHALL devolver HTTP 404 con un mensaje indicando que el docente no fue encontrado.
3. WHEN el cuerpo de la solicitud `PUT` está vacío (`{}`), THE Router SHALL omitir toda modificación y THE API SHALL devolver la representación completa del docente sin cambios con HTTP 200.
4. IF el nuevo `email` ya está asociado a un docente distinto al indicado por `id`, THEN THE API SHALL devolver HTTP 409 con un mensaje indicando el campo `email` como origen del conflicto.
5. IF la nueva `especialidad` ya está asociada a un docente distinto al indicado por `id`, THEN THE API SHALL devolver HTTP 409 con un mensaje indicando el campo `especialidad` como origen del conflicto.
6. WHEN se aplica una actualización parcial, THE CRUD_Layer SHALL preservar sin modificación los valores de todos los campos del docente no incluidos en el cuerpo de la solicitud.
7. IF el valor del campo `email` no cumple el formato RFC 5322, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando que el formato del campo `email` es inválido.
8. IF el `id` en la ruta no es un identificador con formato válido, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando que el formato del identificador es inválido.
9. IF algún campo de texto presente en el cuerpo de la solicitud supera 200 caracteres, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el campo que excede el límite.

---

### Requisito 5: Eliminación de un docente

**User Story:** Como administrador del sistema, quiero eliminar un docente del sistema, para mantener el registro actualizado.

#### Criterios de Aceptación

1. WHEN el cliente envía una solicitud `DELETE /teachers/{id}` con un `id` que existe en la base de datos, THE CRUD_Layer SHALL eliminar permanentemente el registro del docente indicado y THE API SHALL devolver HTTP 200 con un mensaje de confirmación que identifique el `id` eliminado.
2. IF el `id` indicado no corresponde a ningún docente registrado, THEN THE API SHALL devolver HTTP 404 con un mensaje descriptivo sin modificar ningún otro registro.
3. WHEN un docente es eliminado exitosamente, THE API SHALL no incluir el registro eliminado en las respuestas subsiguientes de `GET /teachers` ni de `GET /teachers/{id}`.
4. IF el `id` proporcionado no es un entero válido, THEN THE API SHALL devolver HTTP 422 con un mensaje indicando el campo y la razón del rechazo sin modificar ningún registro.
5. IF la base de datos no está disponible al momento de procesar la solicitud `DELETE /teachers/{id}`, THEN THE API SHALL devolver HTTP 503 con un mensaje que indique que el servicio no está disponible.

---

### Requisito 6: Conexión y pool de conexiones a PostgreSQL

**User Story:** Como operador del sistema, quiero que la conexión a PostgreSQL sea configurable por variables de entorno y use un pool de conexiones, para garantizar resiliencia y rendimiento en producción.

#### Criterios de Aceptación

1. THE Pool_de_Conexiones SHALL ser configurable mediante las variables de entorno `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` o la variable única `DATABASE_URL`.
2. IF una variable de entorno individual (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` o `DB_PASSWORD`) no está definida, THEN THE API SHALL usar el valor predeterminado correspondiente: `localhost`, `5432`, `gac`, `postgres`, `postgres`.
3. THE Pool_de_Conexiones SHALL mantener un mínimo de 1 conexión activa, un máximo de 10 conexiones activas y 20 conexiones en desbordamiento.
4. WHEN una conexión del pool está inactiva por 30 minutos, THE Pool_de_Conexiones SHALL cerrarla y abrir una nueva conexión al volver a necesitarse.
5. WHEN se intenta asignar una conexión del pool, THE Pool_de_Conexiones SHALL verificar que la conexión sigue activa antes de asignarla.
6. WHEN la base de datos no está disponible al iniciar la aplicación, THE API SHALL registrar en consola un mensaje de advertencia que indique la no disponibilidad de la base de datos y el detalle del error, y continuar su arranque.
7. WHEN el cliente consulta `GET /health` y la conexión a PostgreSQL está disponible, THE API SHALL devolver HTTP 200 con un cuerpo JSON que incluya el estado de la conexión como `"ok"`.
8. WHEN el cliente consulta `GET /health` y la conexión a PostgreSQL no está disponible, THE API SHALL devolver HTTP 503 con un cuerpo JSON que incluya el estado de la conexión como `"unavailable"`.

---

### Requisito 7: Script de migración de base de datos

**User Story:** Como desarrollador, quiero un script de migración que cree la tabla de docentes, para poder inicializar el esquema de base de datos de forma reproducible.

#### Criterios de Aceptación

1. THE Migration_Script SHALL crear la tabla `docentes` con las columnas: `id` (serial, clave primaria), `nombre` (varchar 200, not null), `email` (varchar 254, not null, unique), `especialidad` (varchar 200, not null, unique), `fecha_creacion` (timestamptz, not null, default `now()`), `activo` (boolean, not null, default `true`).
2. THE Migration_Script SHALL crear dos índices separados con `IF NOT EXISTS`: uno sobre la columna `email` y otro sobre la columna `especialidad`, para acelerar las búsquedas de unicidad.
3. WHEN el Init_Script es invocado y la migración se ejecuta sin errores, THE Init_Script SHALL reportar el éxito en stdout.
4. WHEN el Init_Script es invocado y la migración produce un error, THE Init_Script SHALL reportar el detalle del error en stderr y terminar con código de salida no-cero.
5. WHERE la tabla `docentes` ya existe, THE Migration_Script SHALL omitir su creación sin producir un error (`CREATE TABLE IF NOT EXISTS`).

---

### Requisito 8: Validación de datos de entrada

**User Story:** Como desarrollador, quiero que la API valide todos los datos de entrada con reglas explícitas, para evitar el almacenamiento de datos incorrectos o maliciosos.

#### Criterios de Aceptación

1. THE Pydantic_Validator SHALL rechazar un `nombre` que, después de eliminar espacios iniciales y finales, resulte en una cadena vacía.
2. THE Pydantic_Validator SHALL rechazar un `nombre` cuya longitud original (antes del trim) supere los 200 caracteres.
3. THE Pydantic_Validator SHALL rechazar un `email` que no cumpla con el formato RFC 5322, específicamente: debe contener exactamente un carácter `@`, el dominio debe tener al menos un punto, y la longitud total no debe superar 254 caracteres.
4. THE Pydantic_Validator SHALL rechazar una `especialidad` que, después de eliminar espacios iniciales y finales, resulte en una cadena vacía.
5. THE Pydantic_Validator SHALL rechazar una `especialidad` cuya longitud original (antes del trim) supere los 200 caracteres.
6. WHEN la validación falla, THE API SHALL devolver HTTP 422 con un cuerpo JSON que contenga el campo `detail` identificando el campo inválido y la regla violada.

---

### Requisito 9: Suite de pruebas unitarias

**User Story:** Como desarrollador, quiero una suite de pruebas unitarias que cubra todos los endpoints y sus casos de error, para garantizar la correctitud del módulo sin depender de PostgreSQL.

#### Criterios de Aceptación

1. THE Test_Suite SHALL cubrir exactamente cinco endpoints: `POST /teachers`, `GET /teachers/{id}`, `GET /teachers`, `PUT /teachers/{id}` y `DELETE /teachers/{id}`.
2. THE Test_Suite SHALL incluir al menos un caso de éxito con código HTTP 201 para `POST /teachers`, al menos un caso de éxito con código HTTP 200 para `GET /teachers/{id}`, `GET /teachers` y `PUT /teachers/{id}`, al menos un caso de éxito con código HTTP 200 para `DELETE /teachers/{id}`, y al menos un caso de error con código HTTP 404, 409 o 422 por endpoint según aplique.
3. THE Test_Suite SHALL usar SQLite en memoria como base de datos de prueba, de modo que ninguna prueba requiera una conexión activa a PostgreSQL para ejecutarse.
4. THE Test_Suite SHALL aislar cada caso de prueba en su propia transacción que se revierte al finalizar dicho caso, de forma que el estado de la base de datos al inicio de cada prueba sea idéntico al estado inicial definido por el fixture de configuración.
5. WHEN se ejecuta `pytest tests/test_teachers.py`, THE Test_Suite SHALL completar la totalidad de los casos en un tiempo máximo de 60 segundos y reportar 0 fallos debidos a ausencia de PostgreSQL.
6. WHEN se ejecuta la Integration_Test_Suite y la variable de entorno `TEST_DATABASE_URL` apunta a una instancia PostgreSQL accesible, THE Integration_Test_Suite SHALL ejecutar todos los casos de integración contra esa base de datos dedicada.
7. IF la variable de entorno `TEST_DATABASE_URL` no está definida o la instancia PostgreSQL no es alcanzable al iniciar la Integration_Test_Suite, THEN THE Integration_Test_Suite SHALL marcar todos los casos de integración como omitidos (`skipped`) con un mensaje que indique que PostgreSQL no está disponible, sin producir fallos en la ejecución.

---

### Requisito 10: Actualización del README

**User Story:** Como desarrollador, quiero que el README incluya documentación del nuevo módulo de docentes, para que cualquier miembro del equipo pueda entender y usar la API rápidamente.

#### Criterios de Aceptación

1. THE README SHALL documentar los cinco endpoints del módulo de docentes con su método HTTP, ruta, descripción y códigos de respuesta (éxito y error).
2. THE README SHALL documentar el modelo de datos del docente con todos sus campos, tipos, longitudes máximas, restricciones de unicidad y valores por defecto.
3. WHEN el README incluye ejemplos de uso con `curl`, THE README SHALL proporcionar al menos un ejemplo por endpoint con datos válidos y la respuesta esperada.
4. THE README SHALL documentar las variables de entorno específicas del módulo de docentes con nombre, propósito, tipo de valor esperado y si son obligatorias u opcionales.
5. WHEN un desarrollador sigue las instrucciones del README para ejecutar el script de migración `init_db.py`, THE README SHALL haber indicado el comando exacto a ejecutar y el resultado esperado en caso de éxito.
6. WHEN un desarrollador sigue las instrucciones del README para ejecutar las pruebas unitarias del módulo de docentes, THE README SHALL haber indicado el comando exacto a ejecutar y el resultado esperado al pasar todas las pruebas.
