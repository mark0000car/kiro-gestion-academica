# Requirements Document

## Introduction

Este documento define los requisitos para refactorizar el proyecto **Sistema de Gestión Académica** desde su estructura plana actual hacia una **arquitectura hexagonal** (también llamada Ports & Adapters). El objetivo es separar claramente el núcleo de negocio (dominio y aplicación) de los mecanismos de entrega (HTTP, base de datos, configuración), garantizando que todos los contratos de la API pública, las validaciones y el comportamiento observable del sistema permanezcan idénticos tras la refactorización.

## Glossary

- **Sistema**: El proyecto FastAPI de gestión académica (`kiro-gestion-academica`).
- **Arquitectura_Hexagonal**: Patrón de diseño que divide el código en capa de Dominio, capa de Aplicación y capa de Infraestructura, comunicadas mediante Puertos e interfaces.
- **Dominio**: Capa que contiene las entidades de negocio (modelos puros, sin dependencias de frameworks).
- **Aplicación**: Capa que contiene los casos de uso y los Puertos (interfaces/protocolos abstractos).
- **Infraestructura**: Capa que contiene los Adaptadores concretos: ORM, API HTTP, configuración, migraciones.
- **Puerto**: Interfaz abstracta (Python `Protocol` o clase abstracta) que define un contrato entre la capa de Aplicación y la Infraestructura.
- **Adaptador**: Implementación concreta de un Puerto. Ejemplos: repositorio SQLAlchemy, router FastAPI.
- **Repositorio**: Adaptador que abstrae el acceso a la base de datos implementando el Puerto de repositorio.
- **Caso_de_Uso**: Función o clase en la capa de Aplicación que orquesta la lógica de negocio invocando Puertos.
- **Contrato_de_API**: Conjunto de rutas, métodos HTTP, esquemas de request/response y códigos de estado ya definidos y probados.
- **Prueba_Unitaria**: Prueba que opera sobre la capa de Aplicación o Dominio usando Repositorios en memoria (sin base de datos real).
- **Prueba_de_Integración**: Prueba que ejerce la pila completa sobre PostgreSQL real.

---

## Requirements

### Requirement 1: Reorganización de la estructura de directorios

**User Story:** Como desarrollador, quiero que el código esté organizado en capas de dominio, aplicación e infraestructura, para que las responsabilidades estén claramente separadas y sea fácil navegar y extender el proyecto.

#### Acceptance Criteria

1. WHEN se ejecuta la migración de estructura, THE Sistema SHALL reubicar todo el código fuente bajo `app/` (excluyendo `app/main.py` y archivos de configuración de entorno) en las subcarpetas `app/domain/`, `app/application/` o `app/infrastructure/`, de forma que no quede ningún módulo `.py` directamente bajo `app/` salvo `app/main.py`.
2. THE Sistema SHALL mantener `app/domain/` como la única capa que aloja entidades de negocio y modelos de datos; un módulo pertenece a esta capa si y solo si no contiene importaciones de módulos de infraestructura (base de datos, HTTP, frameworks externos).
3. THE Sistema SHALL mantener `app/application/` como la única capa que aloja Casos de Uso (clases o funciones que orquestan lógica de negocio invocando entidades de dominio) y Puertos (interfaces o clases abstractas que declaran contratos hacia servicios externos sin importar implementaciones de infraestructura).
4. THE Sistema SHALL mantener `app/infrastructure/` como la única capa que aloja Adaptadores (implementaciones concretas de los Puertos definidos en `app/application/`), incluyendo acceso a base de datos, routers HTTP y carga de configuración de entorno.
5. IF todos los símbolos públicos de `app/crud.py`, `app/models.py` y `app/schemas.py` están accesibles desde sus nuevas ubicaciones en las capas correspondientes, THEN THE Sistema SHALL eliminar los archivos `app/crud.py`, `app/models.py` y `app/schemas.py`. Los archivos eliminados no deben ser reemplazados por módulos alias o re-exportación; la eliminación es definitiva.
6. THE Sistema SHALL mantener `app/main.py` conteniendo únicamente la instanciación de la aplicación FastAPI, el registro de routers y la configuración de middleware, sin lógica de negocio, acceso a datos ni definiciones de modelos.
7. WHEN se completa la migración de estructura, THE Sistema SHALL garantizar que la aplicación arranca sin errores de importación, de forma que todos los módulos que previamente importaban desde `app/crud`, `app/models` o `app/schemas` resuelven sus dependencias desde las nuevas rutas de importación.

---

### Requirement 2: Capa de Dominio

**User Story:** Como desarrollador, quiero que las entidades del negocio estén aisladas de frameworks y bibliotecas externas, para poder razonar sobre la lógica de negocio sin depender de SQLAlchemy ni FastAPI.

#### Acceptance Criteria

1. THE Sistema SHALL crear `app/domain/entities/student.py` con una clase `Estudiante` que represente la entidad estudiante con atributos obligatorios: identificador único (entero autoincremental, valor 0 cuando no ha sido persistido), nombre completo (cadena de máximo 100 caracteres), número de documento, correo electrónico y estado activo (booleano), utilizando únicamente tipos estándar de Python sin decoradores ORM.
2. THE Sistema SHALL crear `app/domain/entities/teacher.py` con una clase `Docente` que represente la entidad docente con atributos obligatorios: identificador único (entero autoincremental, valor 0 cuando no ha sido persistido), nombre completo (cadena de máximo 100 caracteres), número de documento, correo electrónico, especialidad y estado activo (booleano), utilizando únicamente tipos estándar de Python sin decoradores ORM.
3. THE Sistema SHALL crear `app/domain/value_objects.py` con los objetos de valor `Email`, `NumeroDocumento` y `Especialidad`, donde cada clase sea inmutable y exponga su valor mediante un atributo de solo lectura.
4. IF un valor de `Email` se construye con una cadena que no contenga exactamente un símbolo `@`, con prefijo vacío o con dominio sin al menos un punto, THEN THE Sistema SHALL lanzar un `ValueError` con un mensaje que identifique el valor recibido y el motivo del rechazo.
5. IF un valor de `NumeroDocumento` se construye con una cadena que no cumpla el patrón `^[A-Za-z0-9\-]{3,30}$`, THEN THE Sistema SHALL lanzar un `ValueError` con un mensaje que identifique el valor recibido y el motivo del rechazo.
6. IF un valor de `Especialidad` se construye con una cadena vacía o con más de 100 caracteres, THEN THE Sistema SHALL lanzar un `ValueError` con un mensaje que identifique el valor recibido y el límite infringido.
7. THE Sistema SHALL garantizar que las clases de la capa de Dominio no importen módulos de SQLAlchemy, FastAPI, Pydantic ni de la capa de Infraestructura, verificable mediante análisis estático del código fuente.

---

### Requirement 3: Puertos de repositorio (interfaces abstractas)

**User Story:** Como desarrollador, quiero que los casos de uso dependan de interfaces abstractas en lugar de implementaciones concretas, para poder sustituir la base de datos o usarla en pruebas sin modificar la lógica de negocio.

#### Acceptance Criteria

1. THE Sistema SHALL crear `app/application/ports/student_repository.py` con un `Protocol` o clase abstracta `EstudianteRepository` que declare exactamente los métodos: `guardar(estudiante: Estudiante) -> Estudiante`, `obtener_por_id(id: UUID) -> Optional[Estudiante]`, `obtener_por_email(email: str) -> Optional[Estudiante]`, `obtener_por_documento(documento: str) -> Optional[Estudiante]`, `listar(pagina: int, por_pagina: int, solo_activos: Optional[bool]) -> tuple[list[Estudiante], int]`, `eliminar(id: UUID) -> bool`.
2. THE Sistema SHALL crear `app/application/ports/teacher_repository.py` con un `Protocol` o clase abstracta `DocenteRepository` que declare exactamente los métodos: `guardar(docente: Docente) -> Docente`, `obtener_por_id(id: UUID) -> Optional[Docente]`, `obtener_por_email(email: str) -> Optional[Docente]`, `obtener_por_especialidad(especialidad: str) -> List[Docente]`, `listar(pagina: int, por_pagina: int, solo_activos: Optional[bool]) -> tuple[list[Docente], int]`, `eliminar(id: UUID) -> bool`.
3. THE Sistema SHALL garantizar que los Puertos solo importen clases de la capa de Dominio, sin dependencias de SQLAlchemy ni de FastAPI; verificable inspeccionando que ninguna sentencia `import` en los archivos de Puertos referencie módulos de SQLAlchemy o FastAPI.
4. THE Sistema SHALL documentar cada método en los Puertos con un docstring que especifique: descripción de la operación, el tipo y semántica de cada parámetro, el tipo y semántica del valor de retorno, y las excepciones que puede lanzar.
5. IF un método del Puerto no puede completar la operación debido a una violación de contrato de dominio, THEN THE Sistema SHALL propagar la excepción de dominio sin modificarla, sin convertirla en una excepción de infraestructura. Las excepciones originadas en la infraestructura (conexión a BD perdida, error de disco) que no sean excepciones de dominio deberán propagarse sin modificar, sin ser convertidas a excepciones de dominio.
6. IF un método del Puerto no encuentra la entidad solicitada, THEN THE Sistema SHALL retornar `None` (en métodos que retornan `Optional`) o lista vacía (en métodos que retornan `List`), sin lanzar excepción.

---

### Requirement 4: Casos de Uso

**User Story:** Como desarrollador, quiero que la lógica de cada operación CRUD esté encapsulada en Casos_de_Uso independientes, para que cada caso de uso sea testeable de forma aislada inyectando un repositorio en memoria.

#### Acceptance Criteria

1. THE Sistema SHALL crear Casos_de_Uso para estudiantes en `app/application/use_cases/student/`: `crear_estudiante.py`, `obtener_estudiante.py`, `listar_estudiantes.py`, `actualizar_estudiante.py`, `eliminar_estudiante.py`.
2. THE Sistema SHALL crear Casos_de_Uso para docentes en `app/application/use_cases/teacher/`: `crear_docente.py`, `obtener_docente.py`, `listar_docentes.py`, `actualizar_docente.py`, `eliminar_docente.py`.
3. WHEN un Caso_de_Uso recibe datos que incluyen un campo obligatorio ausente, un valor fuera del rango permitido o un tipo incompatible con la entidad de dominio, THE Sistema SHALL lanzar una excepción de dominio específica (no una `HTTPException`) sin persistir ningún cambio en el repositorio.
4. WHEN un Caso_de_Uso intenta recuperar o eliminar una entidad que no existe en el repositorio, THE Sistema SHALL lanzar una excepción `EntidadNoEncontrada` del dominio sin modificar el estado del repositorio.
5. WHEN un Caso_de_Uso intenta crear una entidad con un identificador único duplicado, THE Sistema SHALL lanzar una excepción `ConflictoDeUnicidad` del dominio.
6. THE Sistema SHALL garantizar que los Casos_de_Uso solo importen del Dominio y de los Puertos, sin dependencias de SQLAlchemy ni de FastAPI. No se permiten excepciones a esta regla, incluyendo importaciones selectivas para validación HTTP o manejo de transacciones.
7. WHEN se llama a un Caso_de_Uso de actualización sin proporcionar ningún campo a modificar, THE Sistema SHALL retornar la entidad sin modificaciones y sin ejecutar ninguna operación de escritura en el repositorio.
8. WHEN un Caso_de_Uso de actualización recibe el identificador de una entidad que no existe, THE Sistema SHALL lanzar una excepción `EntidadNoEncontrada` del dominio sin modificar el estado del repositorio.
9. THE Sistema SHALL garantizar que cada Caso_de_Uso recibe el repositorio que necesita a través de su constructor, sin instanciarlo internamente, de forma que sea posible sustituir el repositorio por una implementación en memoria al crear el Caso_de_Uso en los tests.

---

### Requirement 5: Adaptador de persistencia (SQLAlchemy)

**User Story:** Como desarrollador, quiero que el acceso a la base de datos esté confinado en la capa de Infraestructura, para que cambiar el ORM o la base de datos no afecte a los Casos_de_Uso.

#### Acceptance Criteria

1. THE Sistema SHALL crear `app/infrastructure/persistence/models.py` con los modelos ORM SQLAlchemy (`EstudianteORM`, `DocenteORM`) declarando exactamente las columnas presentes en el esquema actual de las tablas `estudiantes` y `docentes`, sin añadir ni eliminar columnas.
2. THE Sistema SHALL crear `app/infrastructure/persistence/student_repository.py` con la clase `SQLAlchemyEstudianteRepository` que implemente el Puerto `EstudianteRepository`, con los métodos: `guardar`, `obtener_por_id`, `obtener_por_email`, `obtener_por_documento`, `listar`, `eliminar`; y que incluya conversión bidireccional entre la entidad de dominio `Estudiante` y el modelo ORM `EstudianteORM`.
3. THE Sistema SHALL crear `app/infrastructure/persistence/teacher_repository.py` con la clase `SQLAlchemyDocenteRepository` que implemente el Puerto `DocenteRepository`, con los métodos: `guardar`, `obtener_por_id`, `obtener_por_email`, `obtener_por_especialidad`, `listar`, `eliminar`; y que incluya conversión bidireccional entre la entidad de dominio `Docente` y el modelo ORM `DocenteORM`.
4. IF `SQLAlchemyEstudianteRepository.guardar` recibe una entidad cuyo email o numero_documento ya existe en la tabla `estudiantes`, THEN THE Sistema SHALL hacer rollback de la sesión, capturar la `IntegrityError` de SQLAlchemy y relanzarla como `ConflictoDeUnicidad` del dominio, sin que la excepción `IntegrityError` se propague fuera de la capa de Infraestructura. IF el rollback de la sesión falla durante este proceso, THE Sistema SHALL igualmente lanzar la excepción `ConflictoDeUnicidad`, garantizando que la capa de aplicación reciba información de error correcta.
5. IF `SQLAlchemyDocenteRepository.guardar` recibe una entidad cuyo email o especialidad ya existe en la tabla `docentes`, THEN THE Sistema SHALL hacer rollback de la sesión, capturar la `IntegrityError` de SQLAlchemy y relanzarla como `ConflictoDeUnicidad` del dominio, sin que la excepción `IntegrityError` se propague fuera de la capa de Infraestructura. IF el rollback de la sesión falla durante este proceso, THE Sistema SHALL igualmente lanzar la excepción `ConflictoDeUnicidad`, garantizando que la capa de aplicación reciba información de error correcta.
6. THE Sistema SHALL mantener el esquema de las tablas `estudiantes` y `docentes` sin emitir sentencias DDL de tipo `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE` ni `CREATE INDEX` durante la migración de código.
7. WHEN un método del repositorio encuentra una excepción que no es `IntegrityError`, THE Sistema SHALL propagar la excepción sin modificarla, delegando el cierre de la sesión al inyector de dependencias.

---

### Requirement 6: Adaptador HTTP (FastAPI routers)

**User Story:** Como desarrollador, quiero que los routers de FastAPI sean adaptadores delgados que traduzcan requests HTTP a llamadas de Casos_de_Uso, para que la lógica de negocio no esté acoplada al framework web.

#### Acceptance Criteria

1. THE Sistema SHALL crear `app/infrastructure/http/routers/students.py` que implemente los 5 endpoints de estudiantes (`POST /students/`, `GET /students/`, `GET /students/{id}`, `PUT /students/{id}`, `DELETE /students/{id}`) sin contener lógica de negocio, delegando toda operación al Caso_de_Uso correspondiente.
2. THE Sistema SHALL crear `app/infrastructure/http/routers/teachers.py` que implemente los 5 endpoints de docentes (`POST /teachers/`, `GET /teachers/`, `GET /teachers/{id}`, `PUT /teachers/{id}`, `DELETE /teachers/{id}`) sin contener lógica de negocio, delegando toda operación al Caso_de_Uso correspondiente.
3. THE Sistema SHALL crear `app/infrastructure/http/schemas/` con esquemas Pydantic separados de request y response para estudiantes y docentes, donde los esquemas de response excluyan campos internos de dominio no destinados al cliente.
4. WHEN un Caso_de_Uso lanza `EntidadNoEncontrada`, THE Sistema SHALL retornar una respuesta HTTP 404 con un cuerpo que contenga un mensaje indicando qué entidad no fue encontrada, sin propagar detalles internos de implementación. IF la misma solicitud pudiera generar tanto un `EntidadNoEncontrada` como un `ConflictoDeUnicidad`, THE Sistema SHALL priorizar la respuesta HTTP 404.
5. WHEN un Caso_de_Uso lanza `ConflictoDeUnicidad`, THE Sistema SHALL retornar una respuesta HTTP 409 con un cuerpo que contenga un mensaje indicando el campo en conflicto, sin propagar detalles internos de implementación.
6. WHEN un Caso_de_Uso lanza una excepción de validación de dominio, THE Sistema SHALL retornar una respuesta HTTP 422 con un cuerpo que contenga un mensaje indicando qué campo o regla de dominio fue violada, sin propagar detalles internos de implementación.
7. THE Sistema SHALL garantizar que todos los endpoints existentes mantengan sus rutas, métodos HTTP, estructura de esquemas de respuesta y códigos de estado de éxito idénticos a los Contratos_de_API definidos previamente, de modo que ningún cliente existente requiera cambios.
8. THE Sistema SHALL mantener los parámetros de paginación `pagina` (entero, mínimo 1), `por_pagina` (entero, entre 1 y 100 inclusive) y `activo` (booleano opcional) en los endpoints de listado, retornando los mismos valores de respuesta y comportamiento de filtrado que los Contratos_de_API existentes.
9. IF un router recibe `pagina` o `por_pagina` con un valor fuera del rango válido, THEN THE Sistema SHALL retornar una respuesta HTTP 422 con un mensaje indicando el parámetro inválido y el rango aceptado, sin invocar el Caso_de_Uso. Los valores en el límite del rango válido (por ejemplo, `pagina=1` con `por_pagina=1`) son aceptados sin error.

---

### Requirement 7: Inyección de dependencias

**User Story:** Como desarrollador, quiero que los repositorios concretos se inyecten en los casos de uso a través del sistema de dependencias de FastAPI, para facilitar la sustitución por mocks en las pruebas y la extensibilidad futura.

#### Acceptance Criteria

1. THE Sistema SHALL crear `app/infrastructure/http/dependencies.py` con funciones proveedoras de dependencias de FastAPI para `EstudianteRepository` y `DocenteRepository`, donde cada función acepte una sesión de base de datos como parámetro y retorne una instancia del repositorio correspondiente.
2. WHEN una solicitud HTTP llega a un router, THE Sistema SHALL inyectar las instancias de repositorio en el Caso_de_Uso exclusivamente mediante `Depends()` de FastAPI, sin instanciarlas directamente en el código del router.
3. WHEN se ejecutan las pruebas unitarias, THE Sistema SHALL permitir sustituir los repositorios reales por implementaciones en memoria mediante `app.dependency_overrides`, sin que las pruebas realicen operaciones sobre la base de datos real.
4. THE Sistema SHALL mantener `app/infrastructure/persistence/database.py` con la función `get_db` que gestione el ciclo de vida de la sesión SQLAlchemy (una sesión por solicitud, cerrada al finalizar), accesible mediante `Depends()` para las funciones proveedoras de dependencias de repositorio.
5. IF la función `get_db` no puede establecer conexión con la base de datos en cualquier momento durante el procesamiento de una solicitud, THEN THE Sistema SHALL propagar la excepción de conexión sin ocultarla, de forma que el endpoint retorne HTTP 503.

---

### Requirement 8: Preservación del comportamiento observable

**User Story:** Como equipo de QA, quiero que todos los tests existentes continúen pasando sin modificaciones, para garantizar que la refactorización no introduzca regresiones en el comportamiento de la API.

#### Acceptance Criteria

1. THE Sistema SHALL mantener todos los tests existentes en `tests/test_students.py` y `tests/test_integration.py` pasando sin modificar el código de los tests, reportando 0 fallos, 0 errores y 0 saltos inesperados al ejecutar `pytest tests/ -v`. A los efectos de este criterio, `tests/conftest.py` no se considera un archivo de test y puede ser actualizado según lo establece el criterio 8.6. Un único fallo de test bloquea la aceptación de la refactorización; no se admiten fallos parciales.
2. IF la base de datos está disponible cuando se llama a `GET /health`, THEN THE Sistema SHALL retornar HTTP 200.
3. IF la base de datos no está disponible cuando se llama a `GET /health`, THEN THE Sistema SHALL retornar HTTP 503.
4. WHEN un cliente realiza `GET /`, THE Sistema SHALL retornar HTTP 200 con `Content-Type: application/json` y el mismo cuerpo de respuesta que la implementación actual.
5. THE Sistema SHALL mantener el mecanismo de override de dependencias en `conftest.py` funcional, de forma que todos los tests que dependen de él continúen pasando sin modificar el código de los tests.
6. IF el mecanismo de inyección de dependencias cambia respecto al actual, THEN THE Sistema SHALL actualizar `tests/conftest.py` de forma que la suite completa reporte 0 fallos y 0 errores tras la actualización.

---

### Requirement 9: Actualización del README.md

**User Story:** Como desarrollador nuevo en el proyecto, quiero que el README.md refleje la nueva estructura hexagonal, para poder entender la organización del código sin tener que explorarlo manualmente.

#### Acceptance Criteria

1. WHEN el desarrollador ejecuta la actualización del README.md, THE Sistema SHALL reemplazar el contenido de la sección "Estructura del proyecto" con un árbol de directorios que refleje la arquitectura hexagonal adoptada, incluyendo todos los directorios de primer y segundo nivel de la nueva estructura.
2. THE Sistema SHALL incluir en el README.md una descripción de entre 2 y 5 oraciones por capa (Dominio, Aplicación e Infraestructura) que identifique qué tipos de componentes contiene cada una y qué responsabilidad cumple dentro de la arquitectura.
3. WHEN el README.md es actualizado, THE Sistema SHALL preservar las secciones de instalación, configuración, ejecución y pruebas reemplazando únicamente los paths que ya no correspondan a la nueva estructura, sin alterar instrucciones ni comandos que no dependan de paths.
4. WHEN el desarrollador ejecuta la actualización del README.md, THE Sistema SHALL agregar una sección dedicada que describa mediante texto el flujo de una solicitud HTTP a través de las capas hexagonales, enumerando en orden secuencial cada capa por la que pasa la solicitud y la acción que realiza en cada una.
5. IF la tabla de endpoints ya existe en el README.md, THEN THE Sistema SHALL preservarla sin modificar ninguna ruta, verbo HTTP ni descripción de los endpoints listados.
6. WHEN el README.md es actualizado, THE Sistema SHALL verificar que todos los paths de archivos y directorios mencionados en el árbol de estructura corresponden a rutas que existen en el sistema de archivos tras completar la migración.
7. WHEN se actualiza el README.md, IF una sección de instalación, configuración, ejecución o pruebas no puede ser preservada, THE Sistema SHALL continuar con la actualización de las demás secciones en lugar de revertir la operación completa.
