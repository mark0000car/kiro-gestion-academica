from typing import Optional, Protocol, runtime_checkable

from app.domain.entities.student import Estudiante


@runtime_checkable
class EstudianteRepository(Protocol):
    """Puerto de repositorio para la entidad Estudiante.

    Define el contrato que deben cumplir todas las implementaciones
    concretas (SQLAlchemy, en memoria para tests, etc.) sin acoplar
    la capa de aplicación a ningún framework de infraestructura.
    """

    def guardar(self, estudiante: Estudiante) -> Estudiante:
        """Inserta o actualiza un estudiante en el almacenamiento.

        - Si ``estudiante.id == 0`` se trata como una inserción y se asigna
          un nuevo identificador al objeto devuelto.
        - Si ``estudiante.id > 0`` se trata como una actualización del
          registro existente.

        Parámetros:
            estudiante: Entidad de dominio con los datos a persistir.

        Devuelve:
            La misma entidad con ``id`` asignado (en caso de inserción).

        Lanza:
            ConflictoDeUnicidad: si ya existe un registro con el mismo
                ``email`` o ``numero_documento``.
        """
        ...

    def obtener_por_id(self, id: int) -> Optional[Estudiante]:
        """Devuelve el estudiante cuyo identificador coincide con ``id``.

        Parámetros:
            id: Identificador entero del estudiante.

        Devuelve:
            La entidad ``Estudiante`` si existe, ``None`` en caso contrario.
        """
        ...

    def obtener_por_email(self, email: str) -> Optional[Estudiante]:
        """Devuelve el estudiante cuyo correo electrónico coincide con ``email``.

        Parámetros:
            email: Dirección de correo electrónico a buscar.

        Devuelve:
            La entidad ``Estudiante`` si existe, ``None`` en caso contrario.
        """
        ...

    def obtener_por_documento(self, documento: str) -> Optional[Estudiante]:
        """Devuelve el estudiante cuyo número de documento coincide con ``documento``.

        Parámetros:
            documento: Número de documento a buscar.

        Devuelve:
            La entidad ``Estudiante`` si existe, ``None`` en caso contrario.
        """
        ...

    def listar(
        self,
        pagina: int = 1,
        por_pagina: int = 10,
        solo_activos: Optional[bool] = None,
    ) -> tuple[list[Estudiante], int]:
        """Devuelve una página de estudiantes junto con el total de registros.

        Parámetros:
            pagina: Número de página basado en 1 (por defecto 1).
            por_pagina: Cantidad máxima de registros por página (por defecto 10).
            solo_activos: Si es ``True`` filtra solo estudiantes activos;
                si es ``False`` solo inactivos; si es ``None`` devuelve todos.

        Devuelve:
            Una tupla ``(lista_de_estudiantes, total)`` donde ``total`` es el
            número total de registros que coinciden con el filtro (sin paginar).
        """
        ...

    def eliminar(self, id: int) -> bool:
        """Elimina el estudiante con el identificador dado.

        Parámetros:
            id: Identificador entero del estudiante a eliminar.

        Devuelve:
            ``True`` si el estudiante existía y fue eliminado,
            ``False`` si no se encontró ningún registro con ese ``id``.
        """
        ...
