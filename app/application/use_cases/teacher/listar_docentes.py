from typing import Optional

from app.application.ports.teacher_repository import DocenteRepository
from app.domain.entities.teacher import Docente


class ListarDocentes:
    def __init__(self, repo: DocenteRepository):
        self._repo = repo

    def ejecutar(
        self,
        pagina: int = 1,
        por_pagina: int = 10,
        solo_activos: Optional[bool] = None,
    ) -> tuple[list[Docente], int]:
        """Devuelve una página de docentes junto con el total de registros.

        Args:
            pagina: Número de página basado en 1 (primera página = 1).
            por_pagina: Cantidad máxima de registros por página.
            solo_activos: Si es ``True``, filtra solo docentes activos; si es
                ``False``, solo inactivos; si es ``None``, devuelve todos.

        Returns:
            Tupla ``(lista_de_docentes, total)`` donde ``total`` es el conteo
            total antes de la paginación.
        """
        return self._repo.listar(
            pagina=pagina,
            por_pagina=por_pagina,
            solo_activos=solo_activos,
        )
