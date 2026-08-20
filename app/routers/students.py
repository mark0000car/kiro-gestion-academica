"""
Router de estudiantes.
Define los 5 endpoints CRUD requeridos.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    EstudianteCreate,
    EstudiantePaginado,
    EstudianteResponse,
    EstudianteUpdate,
)

router = APIRouter(prefix="/students", tags=["Estudiantes"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, estudiante_id: int):
    """Obtiene un estudiante o lanza 404."""
    estudiante = crud.obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con id={estudiante_id} no encontrado.",
        )
    return estudiante


def _handle_integrity_error(exc: IntegrityError) -> HTTPException:
    """Traduce una IntegrityError de PostgreSQL a un 409 con mensaje legible."""
    msg = str(exc.orig).lower()
    if "email" in msg:
        detail = "Ya existe un estudiante registrado con ese email."
    elif "numero_documento" in msg:
        detail = "Ya existe un estudiante registrado con ese número de documento."
    else:
        detail = "Conflicto de datos: el registro ya existe."
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ---------------------------------------------------------------------------
# POST /students
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estudiante",
    responses={
        201: {"description": "Estudiante creado exitosamente."},
        409: {"description": "Email o número de documento ya registrado."},
        422: {"description": "Error de validación en los datos enviados."},
    },
)
def crear_estudiante(datos: EstudianteCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo estudiante en el sistema.

    - **nombre**: Nombre completo (requerido).
    - **direccion**: Dirección de residencia (requerido).
    - **numero_documento**: Documento de identidad único (requerido).
    - **email**: Correo electrónico único (requerido).
    """
    try:
        return crud.crear_estudiante(db, datos)
    except IntegrityError as exc:
        db.rollback()
        raise _handle_integrity_error(exc) from exc


# ---------------------------------------------------------------------------
# GET /students
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=EstudiantePaginado,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los estudiantes (paginado)",
    responses={
        200: {"description": "Lista paginada de estudiantes."},
    },
)
def listar_estudiantes(
    pagina: int = Query(default=1, ge=1, description="Número de página (empieza en 1)."),
    por_pagina: int = Query(default=10, ge=1, le=100, description="Registros por página (máx. 100)."),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo."),
    db: Session = Depends(get_db),
):
    """
    Devuelve la lista de estudiantes con paginación opcional.

    - **pagina**: Número de página (mínimo 1).
    - **por_pagina**: Cantidad de registros por página (1-100).
    - **activo**: Filtrar únicamente activos (`true`) o inactivos (`false`).
    """
    estudiantes, total = crud.listar_estudiantes(db, pagina, por_pagina, activo)
    return EstudiantePaginado(
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        estudiantes=estudiantes,
    )


# ---------------------------------------------------------------------------
# GET /students/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un estudiante por ID",
    responses={
        200: {"description": "Datos del estudiante."},
        404: {"description": "Estudiante no encontrado."},
    },
)
def obtener_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Devuelve los datos completos del estudiante con el **id** indicado."""
    return _get_or_404(db, estudiante_id)


# ---------------------------------------------------------------------------
# PUT /students/{id}
# ---------------------------------------------------------------------------

@router.put(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un estudiante existente",
    responses={
        200: {"description": "Estudiante actualizado o sin cambios (body vacío)."},
        404: {"description": "Estudiante no encontrado."},
        409: {"description": "Email o número de documento ya pertenece a otro estudiante."},
        422: {"description": "Error de validación."},
    },
)
def actualizar_estudiante(
    estudiante_id: int,
    datos: EstudianteUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza uno o más campos del estudiante indicado.
    Solo se modifican los campos enviados en el cuerpo de la solicitud.
    Un body vacío `{}` se trata como no-op y devuelve el estudiante sin cambios.
    """
    estudiante = _get_or_404(db, estudiante_id)
    # Body vacío → no-op: devolver el estudiante sin modificar (Req 4.3)
    if not datos.model_dump(exclude_unset=True):
        return estudiante
    try:
        return crud.actualizar_estudiante(db, estudiante, datos)
    except IntegrityError as exc:
        db.rollback()
        raise _handle_integrity_error(exc) from exc


# ---------------------------------------------------------------------------
# DELETE /students/{id}
# ---------------------------------------------------------------------------

@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un estudiante",
    responses={
        200: {"description": "Estudiante eliminado exitosamente."},
        404: {"description": "Estudiante no encontrado."},
    },
)
def eliminar_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente el estudiante con el **id** indicado."""
    estudiante = _get_or_404(db, estudiante_id)
    crud.eliminar_estudiante(db, estudiante)
    return {"mensaje": f"Estudiante con id={estudiante_id} eliminado exitosamente."}

