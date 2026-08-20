"""
Capa de acceso a datos (repositorio).
Todas las operaciones de base de datos sobre la tabla 'estudiantes'.
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Docente, Estudiante
from app.schemas import DocenteCreate, DocenteUpdate, EstudianteCreate, EstudianteUpdate


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def crear_estudiante(db: Session, datos: EstudianteCreate) -> Estudiante:
    """
    Inserta un nuevo estudiante en la base de datos.
    Lanza IntegrityError si el email o numero_documento ya existen.
    """
    estudiante = Estudiante(
        nombre=datos.nombre,
        direccion=datos.direccion,
        numero_documento=datos.numero_documento,
        email=str(datos.email),
        activo=True,
    )
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def obtener_estudiante_por_id(db: Session, estudiante_id: int) -> Optional[Estudiante]:
    """Devuelve el estudiante con el id dado, o None si no existe."""
    return db.get(Estudiante, estudiante_id)


def obtener_estudiante_por_email(db: Session, email: str) -> Optional[Estudiante]:
    """Devuelve el estudiante con el email dado, o None si no existe."""
    stmt = select(Estudiante).where(Estudiante.email == email)
    return db.scalars(stmt).first()


def obtener_estudiante_por_documento(
    db: Session, numero_documento: str
) -> Optional[Estudiante]:
    """Devuelve el estudiante con el numero_documento dado, o None si no existe."""
    stmt = select(Estudiante).where(Estudiante.numero_documento == numero_documento)
    return db.scalars(stmt).first()


def listar_estudiantes(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 10,
    solo_activos: Optional[bool] = None,
) -> tuple[list[Estudiante], int]:
    """
    Devuelve una tupla (lista de estudiantes, total de registros).

    Args:
        pagina:       Número de página (1-based).
        por_pagina:   Cantidad de registros por página (máx. 100).
        solo_activos: Si se indica, filtra por el campo 'activo'.
    """
    por_pagina = min(por_pagina, 100)
    offset = (pagina - 1) * por_pagina

    base_query = select(Estudiante)
    count_query = select(func.count()).select_from(Estudiante)

    if solo_activos is not None:
        base_query = base_query.where(Estudiante.activo == solo_activos)
        count_query = count_query.where(Estudiante.activo == solo_activos)

    total: int = db.scalar(count_query) or 0

    estudiantes = db.scalars(
        base_query.order_by(Estudiante.id).offset(offset).limit(por_pagina)
    ).all()

    return list(estudiantes), total


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def actualizar_estudiante(
    db: Session, estudiante: Estudiante, datos: EstudianteUpdate
) -> Estudiante:
    """
    Aplica los cambios indicados en 'datos' al objeto 'estudiante' y persiste.
    Solo actualiza los campos que no son None.
    Lanza IntegrityError si el nuevo email o numero_documento ya existen.
    """
    update_data = datos.model_dump(exclude_unset=True)

    for campo, valor in update_data.items():
        # EmailStr puede llegar como objeto; lo convertimos a str
        if campo == "email" and valor is not None:
            valor = str(valor)
        setattr(estudiante, campo, valor)

    db.commit()
    db.refresh(estudiante)
    return estudiante


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def eliminar_estudiante(db: Session, estudiante: Estudiante) -> None:
    """Elimina permanentemente el registro de la base de datos."""
    db.delete(estudiante)
    db.commit()


# ---------------------------------------------------------------------------
# CRUD para Docente
# ---------------------------------------------------------------------------

# CREATE

def crear_docente(db: Session, datos: DocenteCreate) -> Docente:
    """
    Inserta un nuevo docente en la base de datos.
    Lanza IntegrityError si el email o especialidad ya existen.
    """
    docente = Docente(
        nombre=datos.nombre,
        email=str(datos.email),
        especialidad=datos.especialidad,
        activo=True,
    )
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


# READ

def obtener_docente_por_id(db: Session, docente_id: int) -> Optional[Docente]:
    """Devuelve el docente con el id dado, o None si no existe."""
    return db.get(Docente, docente_id)


def obtener_docente_por_email(db: Session, email: str) -> Optional[Docente]:
    """Devuelve el docente con el email dado, o None si no existe."""
    stmt = select(Docente).where(Docente.email == email)
    return db.scalars(stmt).first()


def obtener_docente_por_especialidad(db: Session, especialidad: str) -> Optional[Docente]:
    """Devuelve el docente con la especialidad dada, o None si no existe."""
    stmt = select(Docente).where(Docente.especialidad == especialidad)
    return db.scalars(stmt).first()


def listar_docentes(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 10,
    solo_activos: Optional[bool] = None,
) -> tuple[list[Docente], int]:
    """
    Devuelve una tupla (lista de docentes, total de registros).

    Args:
        pagina:       Número de página (1-based).
        por_pagina:   Cantidad de registros por página (máx. 100).
        solo_activos: Si se indica, filtra por el campo 'activo'.
    """
    por_pagina = min(por_pagina, 100)
    offset = (pagina - 1) * por_pagina

    base_query = select(Docente)
    count_query = select(func.count()).select_from(Docente)

    if solo_activos is not None:
        base_query = base_query.where(Docente.activo == solo_activos)
        count_query = count_query.where(Docente.activo == solo_activos)

    total: int = db.scalar(count_query) or 0

    docentes = db.scalars(
        base_query.order_by(Docente.id).offset(offset).limit(por_pagina)
    ).all()

    return list(docentes), total


# UPDATE

def actualizar_docente(
    db: Session, docente: Docente, datos: DocenteUpdate
) -> Docente:
    """
    Aplica los cambios indicados en 'datos' al objeto 'docente' y persiste.
    Solo actualiza los campos que no son None.
    Lanza IntegrityError si el nuevo email o especialidad ya existen.
    """
    update_data = datos.model_dump(exclude_unset=True)

    for campo, valor in update_data.items():
        # EmailStr puede llegar como objeto; lo convertimos a str
        if campo == "email" and valor is not None:
            valor = str(valor)
        setattr(docente, campo, valor)

    db.commit()
    db.refresh(docente)
    return docente


# DELETE

def eliminar_docente(db: Session, docente: Docente) -> None:
    """Elimina permanentemente el registro de la base de datos."""
    db.delete(docente)
    db.commit()
