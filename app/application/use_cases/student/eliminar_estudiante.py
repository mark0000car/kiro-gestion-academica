from app.application.ports.student_repository import EstudianteRepository
from app.domain.exceptions import EntidadNoEncontrada


class EliminarEstudiante:
    """Caso de uso: eliminar un estudiante por su identificador."""

    def __init__(self, repo: EstudianteRepository):
        self._repo = repo

    def ejecutar(self, id: int) -> None:
        """Elimina el estudiante identificado por ``id``.

        Parámetros:
            id: Identificador entero del estudiante a eliminar.

        Lanza:
            EntidadNoEncontrada: si no existe ningún estudiante con ese ``id``.
        """
        eliminado = self._repo.eliminar(id)
        if not eliminado:
            raise EntidadNoEncontrada("Estudiante", id)
