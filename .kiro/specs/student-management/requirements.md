# Requirements Document

## Introduction

This document specifies the functional and non-functional requirements for the
**Sistema de Gestión de Estudiantes**, a RESTful API built with FastAPI and
PostgreSQL that enables academic institutions to register, query, update, and
delete student records. The system exposes a set of HTTP endpoints consumed by
client applications, enforces data integrity through unique constraints and
field-level validation, and surfaces operational status through dedicated
health-check and documentation endpoints.

---

## Glossary

- **API**: The FastAPI application that processes HTTP requests and responses.
- **Student**: An individual academic record stored in the `estudiantes` table,
  identified by a surrogate integer primary key.
- **Document_Number**: A student''s identity document identifier, composed of
  letters, digits, and hyphens (3-30 characters), unique across all students.
- **Email**: A syntactically valid RFC 5322 email address (max 254 characters), unique across all students.
- **Validator**: The Pydantic v2 layer that enforces field-level rules before
  data reaches the persistence layer.
- **Repository**: The CRUD layer (`crud.py`) that issues SQL statements against
  the PostgreSQL database through SQLAlchemy 2.0.
- **DB**: The PostgreSQL 14+ database instance that persists student records.
- **Connection_Pool**: The SQLAlchemy `QueuePool` that manages reusable
  database connections with a maximum size of 10 active connections and 20
  overflow connections.
- **Pagination**: The mechanism that divides a result set into discrete pages
  identified by a page number and a page size.

---

## Requirements

### Requirement 1: Create a Student

**User Story:** As an academic administrator, I want to register a new student,
so that the student''s data is persisted and available for future queries.

#### Acceptance Criteria

1. WHEN a `POST /students/` request is received with a valid JSON body
   containing `nombre`, `direccion`, `numero_documento`, and `email`, THE API
   SHALL persist a new Student record in the DB and return a `201 Created`
   response with the complete student representation including the
   auto-generated `id`, `fecha_creacion`, and `activo` fields.

2. WHEN a `POST /students/` request is received and the `email` value already
   exists in the DB, THE API SHALL return a `409 Conflict` response with a
   `detail` field whose value contains the word "email".

3. WHEN a `POST /students/` request is received and the `numero_documento`
   value already exists in the DB, THE API SHALL return a `409 Conflict`
   response with a `detail` field whose value contains the word "documento".

4. WHEN a `POST /students/` request is received with a missing required field
   (`nombre`, `direccion`, `numero_documento`, or `email`), THE Validator SHALL
   reject the request and THE API SHALL return a `422 Unprocessable Entity`
   response with field-level error details identifying which field is missing.

5. WHEN a `POST /students/` request is received with an `email` value that does
   not conform to RFC 5322 format, THE Validator SHALL reject the request and
   THE API SHALL return a `422 Unprocessable Entity` response with a
   field-level error identifying `email` as the invalid field.

6. WHEN a `POST /students/` request is received with a `numero_documento` value
   that contains characters other than letters, digits, or hyphens, or whose
   length is outside the range of 3 to 30 characters, THE Validator SHALL
   reject the request and THE API SHALL return a `422 Unprocessable Entity`
   response with a field-level error identifying `numero_documento`.

7. WHEN a `POST /students/` request is received with a `nombre` field whose
   value, after stripping leading and trailing whitespace, is empty or exceeds
   200 characters, THE Validator SHALL reject the request and THE API SHALL
   return a `422 Unprocessable Entity` response with a field-level error
   identifying `nombre`.

8. WHEN a `POST /students/` request is received with a `direccion` field whose
   value, after stripping leading and trailing whitespace, is empty or exceeds
   500 characters, THE Validator SHALL reject the request and THE API SHALL
   return a `422 Unprocessable Entity` response with a field-level error
   identifying `direccion`.

9. WHEN a new Student is created, THE Repository SHALL set the `activo` field
   to `true` and delegate the generation of `fecha_creacion` to the DB server
   timestamp function.

10. FOR ALL valid `EstudianteCreate` payloads `p`, THE API SHALL return a
    response body `r` such that `r.nombre == p.nombre`, `r.email == p.email`,
    `r.numero_documento == p.numero_documento`, and `r.direccion == p.direccion`
    (round-trip property: input fields are preserved in the response).

11. WHEN a `POST /students/` request is received and the DB is unavailable, THE
    API SHALL return a `503 Service Unavailable` response and SHALL NOT persist
    any partial record.

12. WHEN a `POST /students/` request is received with a body that is not valid
    JSON or with a `Content-Type` header other than `application/json`, THE API
    SHALL return a `422 Unprocessable Entity` response.

---

### Requirement 2: Retrieve a Student by ID

**User Story:** As an academic administrator, I want to retrieve the full
details of a specific student by identifier, so that I can view or verify the
student''s record.

#### Acceptance Criteria

1. WHEN a `GET /students/{id}` request is received and a Student with the given
   positive integer `id` exists in the DB, THE API SHALL return a `200 OK`
   response with the complete student representation.

2. WHEN a `GET /students/{id}` request is received and no Student with the
   given `id` exists in the DB, THE API SHALL return a `404 Not Found` response
   with a `detail` field containing the phrase "no encontrado".

3. WHEN a `GET /students/{id}` request is received with a non-integer path
   parameter, THE Validator SHALL reject the request and THE API SHALL return a
   `422 Unprocessable Entity` response.

4. THE API SHALL include the fields `id` (integer), `nombre` (string),
   `direccion` (string), `numero_documento` (string), `email` (string),
   `activo` (boolean), and `fecha_creacion` (ISO 8601 timestamp string) in
   every successful `GET /students/{id}` response.

5. WHEN a `GET /students/{id}` request is received with an `id` value that is
   zero or negative, THE API SHALL return a `404 Not Found` response.

---

### Requirement 3: List Students with Pagination and Filtering

**User Story:** As an academic administrator, I want to retrieve a paginated
and optionally filtered list of students, so that I can browse large datasets
without overloading the client or the server.

#### Acceptance Criteria

1. WHEN a `GET /students/` request is received, THE API SHALL return a `200 OK`
   response with a JSON object containing the fields `total`, `pagina`,
   `por_pagina`, and `estudiantes`.

2. WHEN a `GET /students/` request is received without query parameters, THE
   API SHALL default to `pagina=1` and `por_pagina=10`.

3. WHEN a `GET /students/` request is received with `pagina=N` and
   `por_pagina=M`, THE API SHALL return exactly the students at offset
   `(N-1)*M` up to a maximum of `M` records, ordered by ascending `id`.

4. WHEN a `GET /students/` request is received with a `pagina` value less than
   1 or a non-integer `pagina` value, THE Validator SHALL reject the request
   and THE API SHALL return a `422 Unprocessable Entity` response.

5. WHEN a `GET /students/` request is received with a `por_pagina` value
   greater than 100 or less than 1 or a non-integer `por_pagina` value, THE
   Validator SHALL reject the request and THE API SHALL return a `422
   Unprocessable Entity` response.

6. WHEN a `GET /students/` request is received with `activo=true`, THE API
   SHALL include only Student records whose `activo` field is `true` in the
   response. IF the filtering logic fails and inactive students are included in
   the results, THE API SHALL return an error status rather than a partial or
   incorrect result set.

7. WHEN a `GET /students/` request is received with `activo=false`, THE API
   SHALL include only Student records whose `activo` field is `false` in the
   response.

8. WHEN a `GET /students/` request is received without the `activo` parameter,
   THE API SHALL include all students regardless of their `activo` value.

9. THE `total` field in the list response SHALL reflect the count of records
   that match the applied filter (if any), not the count of records on the
   current page.

10. FOR ALL valid list requests, the sum of the sizes of all pages SHALL equal
    the value of `total` (pagination completeness invariant).

11. WHEN a `GET /students/` request is received with a valid `pagina` value
    that exceeds the number of available pages, THE API SHALL return a `200 OK`
    response with an empty `estudiantes` list and the correct `total` count.

12. WHEN a `GET /students/` request is received with an `activo` query
    parameter that is not a boolean value, THE Validator SHALL reject the
    request and THE API SHALL return a `422 Unprocessable Entity` response.

---

### Requirement 4: Update a Student

**User Story:** As an academic administrator, I want to update one or more
fields of an existing student record, so that the information remains accurate
over time.

#### Acceptance Criteria

1. WHEN a `PUT /students/{id}` request is received with a JSON body containing
   at least one of the fields `nombre`, `direccion`, `numero_documento`,
   `email`, or `activo`, and a Student with the given `id` exists in the DB,
   THE Validator SHALL validate all supplied fields before THE Repository
   applies them to the record.

2. WHEN the Repository applies the supplied fields after successful validation,
   THE API SHALL return a `200 OK` response with the full updated student
   representation containing all fields: `id`, `nombre`, `direccion`,
   `numero_documento`, `email`, `activo`, and `fecha_creacion`.

3. WHEN a `PUT /students/{id}` request is received with an empty JSON object
   `{}` and the Student with the given `id` exists in the DB, THE API SHALL
   treat the request as a successful no-op and return a `200 OK` response with
   the current unmodified student representation.

4. WHEN a `PUT /students/{id}` request is received and no Student with the
   given `id` exists in the DB, THE API SHALL return a `404 Not Found`
   response.

5. WHEN a `PUT /students/{id}` request is received with an `email` value that
   is already assigned to a different Student in the DB, THE API SHALL return a
   `409 Conflict` response with a `detail` field containing the word "email".

6. WHEN a `PUT /students/{id}` request is received with a `numero_documento`
   value that is already assigned to a different Student in the DB, THE API
   SHALL return a `409 Conflict` response with a `detail` field containing the
   word "documento", and SHALL NOT update any field of the target Student record.

7. WHEN a `PUT /students/{id}` request is received with an `email` value that
   does not conform to RFC 5322 format or exceeds 254 characters, THE Validator
   SHALL reject the request and THE API SHALL return a `422 Unprocessable
   Entity` response with a field-level error identifying `email`.

8. WHEN a `PUT /students/{id}` request is received with a `numero_documento`
   value that does not match `^[A-Za-z0-9\-]{3,30}$`, THE Validator SHALL
   reject the request and THE API SHALL return a `422 Unprocessable Entity`
   response with a field-level error identifying `numero_documento`.

9. WHEN a `PUT /students/{id}` request updates a subset of fields, THE
   Repository SHALL preserve the values of all fields not included in the
   request body (partial update invariant).

---

### Requirement 5: Delete a Student

**User Story:** As an academic administrator, I want to permanently remove a
student record from the system, so that obsolete data is not retained.

#### Acceptance Criteria

1. WHEN a `DELETE /students/{id}` request is received and a Student with the
   given positive integer `id` exists in the DB, THE Repository SHALL
   permanently remove the record from the DB.

2. WHEN the Repository removes the record, THE API SHALL return a `200 OK`
   response with a JSON body containing a `mensaje` field whose value includes
   the deleted student''s `id`.

3. WHEN a `DELETE /students/{id}` request is received and no Student with the
   given `id` exists in the DB, THE API SHALL return a `404 Not Found`
   response.

4. WHEN a `DELETE /students/{id}` request is received with a non-positive
   integer or non-integer path parameter, THE Validator SHALL reject the
   request and THE API SHALL return a `422 Unprocessable Entity` response.

5. WHEN a Student record is successfully removed from the DB by THE Repository,
   THE total count of students returned by `GET /students/` SHALL decrease by
   exactly 1 (deletion count invariant). IF the deletion attempt fails or the
   Student does not exist, THE count SHALL remain unchanged.

6. WHEN a Student is deleted, a subsequent `GET /students/{id}` request for the
   same `id` SHALL return `404 Not Found` (deletion visibility invariant).

---

### Requirement 6: Data Validation

**User Story:** As a system integrator, I want all input data to be validated
before persistence, so that invalid or malformed data never reaches the
database.

#### Acceptance Criteria

1. THE Validator SHALL enforce that `nombre` is a non-empty string of at most
   200 characters after stripping leading and trailing whitespace.

2. THE Validator SHALL enforce that `direccion` is a non-empty string of at
   most 500 characters after stripping leading and trailing whitespace.

3. THE Validator SHALL enforce that `numero_documento` matches the regular
   expression `^[A-Za-z0-9\-]{3,30}$`.

4. THE Validator SHALL enforce that `email` conforms to RFC 5322 format and
   does not exceed 254 characters.

5. WHEN one or more field-level validation rules are violated in a single
   request, THE Validator SHALL include a descriptive error message for each
   violated constraint, identifying both the constraint and the affected field.

6. WHEN a valid payload is serialized and deserialized by the Validator, THE
   resulting object SHALL be structurally equal to the original input
   (deterministic round-trip property). IF both serialization and
   deserialization complete successfully, THE operation SHALL be considered
   valid regardless of any intermediate validation flags raised during the
   process.

---

### Requirement 7: Unique Constraints

**User Story:** As a system integrator, I want the system to enforce uniqueness
of email and document number across all student records, so that duplicate
identities are prevented.

#### Acceptance Criteria

1. THE DB SHALL enforce a unique index on the `email` column of the
   `estudiantes` table.

2. THE DB SHALL enforce a unique index on the `numero_documento` column of the
   `estudiantes` table.

3. WHEN a database integrity constraint violation occurs on `email` or
   `numero_documento`, THE Repository SHALL propagate an `IntegrityError` to
   the router layer.

4. WHEN the router layer receives an `IntegrityError` from the Repository, THE
   API SHALL translate it to a `409 Conflict` response with a `detail` field
   identifying the duplicated field by name.

---

### Requirement 8: Connection Pool Management

**User Story:** As a system operator, I want the API to manage database
connections efficiently, so that concurrent requests do not exhaust database
resources.

#### Acceptance Criteria

1. THE Connection_Pool SHALL maintain a maximum of 10 active connections to the
   DB at any given time.

2. THE Connection_Pool SHALL allow up to 20 additional overflow connections
   during peak demand.

3. THE Connection_Pool SHALL validate each connection before use with a
   pre-ping check.

4. THE Connection_Pool SHALL recycle idle connections after 1800 seconds (30
   minutes) to avoid stale connection errors.

5. WHEN a request completes or raises an exception, THE API SHALL close the
   database session and return it to the Connection_Pool, regardless of whether
   the request succeeded or failed. Requests that hang indefinitely without
   completing or raising an exception are outside the scope of this session-
   close guarantee.

6. WHEN all connections in the Connection_Pool are exhausted and the overflow
   limit is reached, THE API SHALL wait up to 30 seconds for a connection to
   become available before raising a timeout error to the caller.

---

### Requirement 9: Health Check and Operational Endpoints

**User Story:** As a system operator, I want dedicated endpoints to verify
system health and access documentation, so that I can monitor the service and
onboard integrators quickly.

#### Acceptance Criteria

1. WHEN a `GET /health` request is received and the DB is reachable, THE API
   SHALL return a `200 OK` response with a JSON body containing exactly
   `{"api": "ok", "base_de_datos": "ok"}`.

2. WHEN a `GET /health` request is received and the DB is not reachable, THE
   API SHALL return a `503 Service Unavailable` response with a JSON body
   containing exactly `{"api": "ok", "base_de_datos": "error"}`.

3. WHEN a `GET /` request is received, THE API SHALL return a `200 OK`
   response with a JSON body containing non-empty string values for the fields
   `mensaje`, `version`, `docs`, and `redoc`, regardless of the state of the
   database or any other downstream dependency.

4. WHEN a `GET /docs` request is received, THE API SHALL return a `200 OK`
   response with `Content-Type: text/html` and a body containing Swagger UI
   markup.

5. WHEN a `GET /openapi.json` request is received, THE API SHALL return a
   `200 OK` response with a valid OpenAPI 3.x JSON schema containing the
   `openapi` and `paths` fields.

---

### Requirement 10: Cross-Origin Resource Sharing (CORS)

**User Story:** As a front-end developer, I want the API to permit cross-origin
requests from any origin during development, so that browser-based clients can
consume the API without proxy configuration.

#### Acceptance Criteria

1. THE API SHALL include the `Access-Control-Allow-Origin: *` response header
   on all responses to allow requests from any origin.

2. WHEN a CORS preflight `OPTIONS` request is received, THE API SHALL return a
   `200 OK` response with the headers `Access-Control-Allow-Methods` and
   `Access-Control-Allow-Headers` set to permit all methods and headers.

---

### Requirement 11: Error Responses

**User Story:** As an API consumer, I want all error responses to include a
structured message body, so that clients can programmatically identify the
reason for a failure.

#### Acceptance Criteria

1. IF a `404 Not Found` response is returned, THEN THE API SHALL include a
   `detail` field in the JSON body with a message that contains the phrase "no
   encontrado".

2. IF a `409 Conflict` response is returned due to a duplicate email, THEN THE
   API SHALL include a `detail` field in the JSON body with a message that
   contains the word "email".

3. IF a `409 Conflict` response is returned due to a duplicate document number,
   THEN THE API SHALL include a `detail` field in the JSON body with a message
   that contains the word "documento".

4. IF a `400 Bad Request` response is returned due to a malformed request
   (excluding empty update bodies, which are treated as no-ops per Requirement
   4.3), THEN THE API SHALL include a `detail` field in the JSON body
   describing the reason for rejection.

5. IF a `422 Unprocessable Entity` response is returned, THEN THE API SHALL
   include field-level error details that identify each invalid field and the
   violated constraint, and SHALL collect all validation errors in a single
   response rather than short-circuiting at the first error.

