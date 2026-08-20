-- =============================================================================
-- Migración: Crear tabla de estudiantes
-- Base de datos: gac
-- =============================================================================

-- Crear la base de datos si no existe (ejecutar como superusuario)
-- CREATE DATABASE gac;

-- Conectarse a la base de datos 'gac' antes de ejecutar el resto:
-- \c gac

-- -----------------------------------------------------------------------------
-- Tabla principal: estudiantes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estudiantes (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(200)        NOT NULL,
    direccion        VARCHAR(500)        NOT NULL,
    numero_documento VARCHAR(30)         NOT NULL,
    email            VARCHAR(254)        NOT NULL,
    fecha_creacion   TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    activo           BOOLEAN             NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_estudiantes_email            UNIQUE (email),
    CONSTRAINT uq_estudiantes_numero_documento UNIQUE (numero_documento)
);

-- Índices para acelerar búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_estudiantes_email            ON estudiantes (email);
CREATE INDEX IF NOT EXISTS idx_estudiantes_numero_documento ON estudiantes (numero_documento);
CREATE INDEX IF NOT EXISTS idx_estudiantes_activo           ON estudiantes (activo);

-- Comentarios de columnas
COMMENT ON TABLE  estudiantes                    IS 'Registro de estudiantes del sistema académico';
COMMENT ON COLUMN estudiantes.id                 IS 'Identificador único autogenerado';
COMMENT ON COLUMN estudiantes.nombre             IS 'Nombre completo del estudiante';
COMMENT ON COLUMN estudiantes.direccion          IS 'Dirección de residencia';
COMMENT ON COLUMN estudiantes.numero_documento   IS 'Número de documento de identidad (único)';
COMMENT ON COLUMN estudiantes.email              IS 'Correo electrónico (único)';
COMMENT ON COLUMN estudiantes.fecha_creacion     IS 'Fecha y hora de registro (UTC)';
COMMENT ON COLUMN estudiantes.activo             IS 'Indica si el estudiante está activo en el sistema';
