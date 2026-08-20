"""
Router de docentes.
Define los 5 endpoints CRUD requeridos.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    DocenteCreate,
    DocentePaginado,
    DocenteResponse,
    DocenteUpdate,
)

router = APIRouter(prefix="/teachers", tags=["Docentes"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, docente_id: int):
    """Obtiene un docente o lanza 404."""
    docente = crud.obtener_docente_por_id(db, docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con id={docente_id} no encontrado.",
        )
    return docente


def _handle_integrity_error(exc: IntegrityError) -> HTTPException:
    """Traduce una IntegrityError de PostgreSQL a un 409 con mensaje legible."""
    msg = str(exc.orig).lower()
    if "email" in msg:
        detail = "Ya existe un docente registrado con ese email."
    elif "especialidad" in msg:
        detail = "Ya existe un docente registrado con esa especialidad."
    else:
        detail = "Conflicto de datos: el registro ya existe."
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ---------------------------------------------------------------------------
# POST /teachers
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=DocenteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo docente",
    responses={
        201: {"description": "Docente creado exitosamente."},
        409: {"description": "Email o especialidad ya registrada."},
        422: {"description": "Error de validación en los datos enviados."},
    },
)
def crear_docente(datos: DocenteCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo docente en el sistema.

    - **nombre**: Nombre completo (requerido).
    - **email**: Correo electrónico único (requerido).
    - **especialidad**: Área de especialización única (requerido).
    """
    try:
        return crud.crear_docente(db, datos)
    except IntegrityError as exc:
        db.rollback()
        raise _handle_integrity_error(exc) from exc


# ---------------------------------------------------------------------------
# GET /teachers
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=DocentePaginado,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los docentes (paginado)",
    responses={
        200: {"description": "Lista paginada de docentes."},
    },
)
def listar_docentes(
    pagina: int = Query(default=1, ge=1, description="Número de página (empieza en 1)."),
    por_pagina: int = Query(default=10, ge=1, le=100, description="Registros por página (máx. 100)."),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo/inactivo."),
    db: Session = Depends(get_db),
):
    """
    Devuelve la lista de docentes con paginación opcional.

    - **pagina**: Número de página (mínimo 1).
    - **por_pagina**: Cantidad de registros por página (1-100).
    - **activo**: Filtrar únicamente activos (`true`) o inactivos (`false`).
    """
    docentes, total = crud.listar_docentes(db, pagina, por_pagina, activo)
    return DocentePaginado(
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        docentes=docentes,
    )


# ---------------------------------------------------------------------------
# GET /teachers/{id}
# ---------------------------------------------------------------------------

@router.get(
    "/{docente_id}",
    response_model=DocenteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un docente por ID",
    responses={
        200: {"description": "Datos del docente."},
        404: {"description": "Docente no encontrado."},
    },
)
def obtener_docente(docente_id: int, db: Session = Depends(get_db)):
    """Devuelve los datos completos del docente con el **id** indicado."""
    return _get_or_404(db, docente_id)


# ---------------------------------------------------------------------------
# PUT /teachers/{id}
# ---------------------------------------------------------------------------

@router.put(
    "/{docente_id}",
    response_model=DocenteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un docente existente",
    responses={
        200: {"description": "Docente actualizado o sin cambios (body vacío)."},
        404: {"description": "Docente no encontrado."},
        409: {"description": "Email o especialidad ya pertenece a otro docente."},
        422: {"description": "Error de validación."},
    },
)
def actualizar_docente(
    docente_id: int,
    datos: DocenteUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualiza uno o más campos del docente indicado.
    Solo se modifican los campos enviados en el cuerpo de la solicitud.
    Un body vacío `{}` se trata como no-op y devuelve el docente sin cambios.
    """
    docente = _get_or_404(db, docente_id)
    # Body vacío → no-op: devolver el docente sin modificar
    if not datos.model_dump(exclude_unset=True):
        return docente
    try:
        return crud.actualizar_docente(db, docente, datos)
    except IntegrityError as exc:
        db.rollback()
        raise _handle_integrity_error(exc) from exc


# ---------------------------------------------------------------------------
# DELETE /teachers/{id}
# ---------------------------------------------------------------------------

@router.delete(
    "/{docente_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un docente",
    responses={
        200: {"description": "Docente eliminado exitosamente."},
        404: {"description": "Docente no encontrado."},
    },
)
def eliminar_docente(docente_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente el docente con el **id** indicado."""
    docente = _get_or_404(db, docente_id)
    crud.eliminar_docente(db, docente)
    return {"mensaje": f"Docente con id={docente_id} eliminado exitosamente."}
