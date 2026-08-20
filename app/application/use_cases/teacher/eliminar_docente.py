from app.application.ports.teacher_repository import DocenteRepository
from app.domain.exceptions import EntidadNoEncontrada


class EliminarDocente:
    def __init__(self, repo: DocenteRepository):
        self._repo = repo

    def ejecutar(self, id: int) -> None:
        """Elimina el docente con el identificador dado.

        Args:
            id: Clave primaria del docente a eliminar.

        Raises:
            EntidadNoEncontrada: Si no existe ningún docente con ese ``id``.
        """
        eliminado = self._repo.eliminar(id)
        if not eliminado:
            raise EntidadNoEncontrada("Docente", id)
