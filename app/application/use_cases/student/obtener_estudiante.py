from app.application.ports.student_repository import EstudianteRepository
from app.domain.entities.student import Estudiante
from app.domain.exceptions import EntidadNoEncontrada


class ObtenerEstudiante:
    """Caso de uso: obtener un estudiante por su identificador."""

    def __init__(self, repo: EstudianteRepository):
        self._repo = repo

    def ejecutar(self, id: int) -> Estudiante:
        """Recupera un estudiante por su ``id``.

        Parámetros:
            id: Identificador entero del estudiante.

        Devuelve:
            La entidad ``Estudiante`` correspondiente.

        Lanza:
            EntidadNoEncontrada: si no existe ningún estudiante con ese ``id``.
        """
        estudiante = self._repo.obtener_por_id(id)
        if estudiante is None:
            raise EntidadNoEncontrada("Estudiante", id)
        return estudiante
