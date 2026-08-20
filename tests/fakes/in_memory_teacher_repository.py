from dataclasses import replace
from typing import Optional

from app.domain.entities.teacher import Docente
from app.domain.exceptions import ConflictoDeUnicidad


class InMemoryDocenteRepository:
    """Implementación en memoria de DocenteRepository para uso en tests.

    No requiere base de datos ni framework web. Aplica las mismas reglas de
    unicidad que la implementación SQLAlchemy real: unicidad sobre `email` y
    `especialidad`.
    """

    def __init__(self):
        self._store: dict[int, Docente] = {}
        self._next_id = 1

    def guardar(self, d: Docente) -> Docente:
        """Inserta o actualiza un docente.

        Si `d.id == 0` se trata como inserción y se asigna un nuevo id
        autoincremental. Si `d.id > 0` se sobreescribe el registro existente.
        Lanza `ConflictoDeUnicidad` si otro registro ya tiene el mismo `email`
        o `especialidad`.
        """
        for existing in self._store.values():
            if existing.id != d.id:
                if existing.email == d.email:
                    raise ConflictoDeUnicidad("email", d.email)
                if existing.especialidad == d.especialidad:
                    raise ConflictoDeUnicidad("especialidad", d.especialidad)

        if d.id == 0:
            d = replace(d, id=self._next_id)
            self._next_id += 1

        self._store[d.id] = d
        return d

    def obtener_por_id(self, id: int) -> Optional[Docente]:
        """Devuelve el docente con el id dado, o None si no existe."""
        return self._store.get(id)

    def obtener_por_email(self, email: str) -> Optional[Docente]:
        """Devuelve el docente con el email dado, o None si no existe."""
        for d in self._store.values():
            if d.email == email:
                return d
        return None

    def obtener_por_especialidad(self, especialidad: str) -> list[Docente]:
        """Devuelve todos los docentes con la especialidad dada."""
        return [d for d in self._store.values() if d.especialidad == especialidad]

    def listar(
        self,
        pagina: int = 1,
        por_pagina: int = 10,
        solo_activos: Optional[bool] = None,
    ) -> tuple[list[Docente], int]:
        """Devuelve (lista paginada, total).

        `pagina` es 1-based. Si `solo_activos` no es None filtra por `activo`.
        El total refleja el conteo tras aplicar el filtro de activos, antes de
        la paginación.
        """
        items = list(self._store.values())
        if solo_activos is not None:
            items = [d for d in items if d.activo == solo_activos]
        total = len(items)
        start = (pagina - 1) * por_pagina
        return items[start : start + por_pagina], total

    def eliminar(self, id: int) -> bool:
        """Elimina el docente con el id dado.

        Devuelve True si existía y fue eliminado, False si no existía.
        """
        if id in self._store:
            del self._store[id]
            return True
        return False
