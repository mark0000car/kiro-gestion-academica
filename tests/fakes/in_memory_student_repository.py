from dataclasses import replace
from typing import Optional

from app.domain.entities.student import Estudiante
from app.domain.exceptions import ConflictoDeUnicidad


class InMemoryEstudianteRepository:
    """Implementación en memoria de EstudianteRepository para uso en tests.

    No requiere base de datos ni framework web. Aplica las mismas reglas de
    unicidad que la implementación SQLAlchemy real.
    """

    def __init__(self):
        self._store: dict[int, Estudiante] = {}
        self._next_id = 1

    def guardar(self, e: Estudiante) -> Estudiante:
        """Inserta o actualiza un estudiante.

        Si `e.id == 0` se trata como inserción y se asigna un nuevo id
        autoincremental. Si `e.id > 0` se sobreescribe el registro existente.
        Lanza `ConflictoDeUnicidad` si otro registro ya tiene el mismo `email`
        o `numero_documento`.
        """
        for existing in self._store.values():
            if existing.id != e.id:
                if existing.email == e.email:
                    raise ConflictoDeUnicidad("email", e.email)
                if existing.numero_documento == e.numero_documento:
                    raise ConflictoDeUnicidad("numero_documento", e.numero_documento)

        if e.id == 0:
            e = replace(e, id=self._next_id)
            self._next_id += 1

        self._store[e.id] = e
        return e

    def obtener_por_id(self, id: int) -> Optional[Estudiante]:
        """Devuelve el estudiante con el id dado, o None si no existe."""
        return self._store.get(id)

    def obtener_por_email(self, email: str) -> Optional[Estudiante]:
        """Devuelve el estudiante con el email dado, o None si no existe."""
        for e in self._store.values():
            if e.email == email:
                return e
        return None

    def obtener_por_documento(self, documento: str) -> Optional[Estudiante]:
        """Devuelve el estudiante con el numero_documento dado, o None si no existe."""
        for e in self._store.values():
            if e.numero_documento == documento:
                return e
        return None

    def listar(
        self,
        pagina: int = 1,
        por_pagina: int = 10,
        solo_activos: Optional[bool] = None,
    ) -> tuple[list[Estudiante], int]:
        """Devuelve (lista paginada, total).

        `pagina` es 1-based. Si `solo_activos` no es None filtra por `activo`.
        El total refleja el conteo tras aplicar el filtro de activos, antes de
        la paginación, replicando el comportamiento de la implementación SQL.
        """
        items = list(self._store.values())
        if solo_activos is not None:
            items = [e for e in items if e.activo == solo_activos]
        total = len(items)
        start = (pagina - 1) * por_pagina
        return items[start : start + por_pagina], total

    def eliminar(self, id: int) -> bool:
        """Elimina el estudiante con el id dado.

        Devuelve True si existía y fue eliminado, False si no existía.
        """
        if id in self._store:
            del self._store[id]
            return True
        return False
