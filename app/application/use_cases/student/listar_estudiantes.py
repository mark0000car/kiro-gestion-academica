from typing import Optional

from app.application.ports.student_repository import EstudianteRepository
from app.domain.entities.student import Estudiante


class ListarEstudiantes:
    """Caso de uso: listar estudiantes con paginación y filtro opcional."""

    def __init__(self, repo: EstudianteRepository):
        self._repo = repo

    def ejecutar(
        self,
        pagina: int = 1,
        por_pagina: int = 10,
        solo_activos: Optional[bool] = None,
    ) -> tuple[list[Estudiante], int]:
        """Devuelve una página de estudiantes y el total de registros.

        Parámetros:
            pagina: Número de página basado en 1 (por defecto 1).
            por_pagina: Cantidad máxima de registros por página (por defecto 10).
            solo_activos: Si es ``True`` filtra solo activos; ``False`` solo
                inactivos; ``None`` devuelve todos.

        Devuelve:
            Una tupla ``(lista_de_estudiantes, total)`` donde ``total`` es el
            conteo total sin paginar que coincide con el filtro.
        """
        return self._repo.listar(
            pagina=pagina,
            por_pagina=por_pagina,
            solo_activos=solo_activos,
        )
