"""
Esquemas Pydantic para validación de datos de entrada y salida.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


class EstudianteBase(BaseModel):
    """Campos comunes compartidos entre creación y actualización."""
    nombre: str
    direccion: str
    numero_documento: str
    email: EmailStr

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 200:
            raise ValueError("El nombre no puede superar los 200 caracteres.")
        return v

    @field_validator("direccion")
    @classmethod
    def direccion_no_vacia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La dirección no puede estar vacía.")
        return v

    @field_validator("numero_documento")
    @classmethod
    def documento_valido(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El número de documento no puede estar vacío.")
        if not re.match(r"^[A-Za-z0-9\-]{3,30}$", v):
            raise ValueError(
                "El número de documento solo puede contener letras, números y guiones (3-30 caracteres)."
            )
        return v


class EstudianteCreate(EstudianteBase):
    """Esquema para crear un nuevo estudiante (POST)."""
    pass


class EstudianteUpdate(BaseModel):
    """Esquema para actualizar un estudiante (PUT). Todos los campos son opcionales."""
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    numero_documento: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío.")
            if len(v) > 200:
                raise ValueError("El nombre no puede superar los 200 caracteres.")
        return v

    @field_validator("direccion")
    @classmethod
    def direccion_no_vacia(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("La dirección no puede estar vacía.")
        return v

    @field_validator("numero_documento")
    @classmethod
    def documento_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not re.match(r"^[A-Za-z0-9\-]{3,30}$", v):
                raise ValueError(
                    "El número de documento solo puede contener letras, números y guiones (3-30 caracteres)."
                )
        return v


class EstudianteResponse(EstudianteBase):
    """Esquema de respuesta completo al consultar un estudiante."""
    id: int
    activo: bool
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class EstudiantePaginado(BaseModel):
    """Respuesta paginada para el listado de estudiantes."""
    total: int
    pagina: int
    por_pagina: int
    estudiantes: list[EstudianteResponse]


# ---------------------------------------------------------------------------
# Schemas para Docente
# ---------------------------------------------------------------------------

class DocenteBase(BaseModel):
    """Campos comunes compartidos entre creación y actualización de docentes."""
    nombre: str
    email: EmailStr
    especialidad: str

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 200:
            raise ValueError("El nombre no puede superar los 200 caracteres.")
        return v

    @field_validator("especialidad")
    @classmethod
    def especialidad_no_vacia(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La especialidad no puede estar vacía.")
        if len(v) > 200:
            raise ValueError("La especialidad no puede superar los 200 caracteres.")
        return v


class DocenteCreate(DocenteBase):
    """Esquema para crear un nuevo docente (POST)."""
    pass


class DocenteUpdate(BaseModel):
    """Esquema para actualizar un docente (PUT). Todos los campos son opcionales."""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    especialidad: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío.")
            if len(v) > 200:
                raise ValueError("El nombre no puede superar los 200 caracteres.")
        return v

    @field_validator("especialidad")
    @classmethod
    def especialidad_no_vacia(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("La especialidad no puede estar vacía.")
            if len(v) > 200:
                raise ValueError("La especialidad no puede superar los 200 caracteres.")
        return v


class DocenteResponse(DocenteBase):
    """Esquema de respuesta completo al consultar un docente."""
    id: int
    activo: bool
    fecha_creacion: datetime

    model_config = {"from_attributes": True}


class DocentePaginado(BaseModel):
    """Respuesta paginada para el listado de docentes."""
    total: int
    pagina: int
    por_pagina: int
    docentes: list[DocenteResponse]
