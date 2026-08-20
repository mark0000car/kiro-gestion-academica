from app.application.ports.teacher_repository import DocenteRepository
from app.domain.entities.teacher import Docente
from app.domain.exceptions import EntidadNoEncontrada


class ObtenerDocente:
    def __init__(self, repo: DocenteRepository):
        self._repo = repo

    def ejecutar(self, id: int) -> Docente:
        """Obtiene un docente por su identificador.

        Args:
            id: Clave primaria del docente a recuperar.

        Returns:
            La entidad ``Docente`` correspondiente al ``id`` dado.

        Raises:
            EntidadNoEncontrada: Si no existe ningún docente con ese ``id``.
        """
        docente = self._repo.obtener_por_id(id)
        if docente is None:
            raise EntidadNoEncontrada("Docente", id)
        return docente
