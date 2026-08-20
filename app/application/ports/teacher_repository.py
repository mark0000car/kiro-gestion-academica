from typing import List, Optional, Protocol, runtime_checkable

from app.domain.entities.teacher import Docente


@runtime_checkable
class DocenteRepository(Protocol):
    """Puerto de repositorio para la entidad Docente.

    Define el contrato que cualquier implementación de persistencia debe cumplir.
    No contiene ninguna dependencia de SQLAlchemy, FastAPI ni Pydantic.
    """

    def guardar(self, docente: Docente) -> Docente:
        """Inserta o actualiza un docente en el repositorio.

        Si ``docente.id == 0`` se trata como una inserción y el repositorio
        asigna un nuevo identificador; de lo contrario se trata como una
        actualización del registro existente.

        Args:
            docente: Entidad ``Docente`` a persistir.

        Returns:
            La entidad ``Docente`` con el ``id`` asignado o actualizado.

        Raises:
            ConflictoDeUnicidad: Si ya existe un docente con el mismo ``email``
                o la misma ``especialidad``.
        """
        ...

    def obtener_por_id(self, id: int) -> Optional[Docente]:
        """Devuelve el docente que corresponde al identificador dado.

        Args:
            id: Clave primaria del docente.

        Returns:
            La entidad ``Docente`` si existe, o ``None`` en caso contrario.
        """
        ...

    def obtener_por_email(self, email: str) -> Optional[Docente]:
        """Devuelve el docente con el email dado.

        Args:
            email: Dirección de correo electrónico a buscar.

        Returns:
            La entidad ``Docente`` si existe, o ``None`` en caso contrario.
        """
        ...

    def obtener_por_especialidad(self, especialidad: str) -> List[Docente]:
        """Devuelve la lista de docentes que tienen la especialidad indicada.

        Args:
            especialidad: Nombre de la especialidad a buscar.

        Returns:
            Lista de entidades ``Docente`` con esa especialidad; lista vacía si
            no hay ninguno.
        """
        ...

    def listar(
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
            total de registros antes de la paginación.
        """
        ...

    def eliminar(self, id: int) -> bool:
        """Elimina el docente con el identificador dado.

        Args:
            id: Clave primaria del docente a eliminar.

        Returns:
            ``True`` si el docente existía y fue eliminado, ``False`` si no se
            encontró ningún registro con ese ``id``.
        """
        ...
