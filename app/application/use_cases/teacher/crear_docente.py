from app.application.ports.teacher_repository import DocenteRepository
from app.domain.entities.teacher import Docente
from app.domain.exceptions import ConflictoDeUnicidad


class CrearDocente:
    def __init__(self, repo: DocenteRepository):
        self._repo = repo

    def ejecutar(self, nombre: str, email: str, especialidad: str) -> Docente:
        """Crea un nuevo docente tras verificar unicidad de email y especialidad.

        Args:
            nombre: Nombre completo del docente.
            email: Dirección de correo electrónico (debe ser única).
            especialidad: Especialidad del docente (debe ser única).

        Returns:
            La entidad ``Docente`` persistida con su ``id`` asignado.

        Raises:
            ConflictoDeUnicidad: Si ya existe un docente con el mismo ``email``
                o la misma ``especialidad``.
        """
        if self._repo.obtener_por_email(email):
            raise ConflictoDeUnicidad("email", email)
        if self._repo.obtener_por_especialidad(especialidad):
            raise ConflictoDeUnicidad("especialidad", especialidad)
        docente = Docente(
            nombre=nombre,
            email=email,
            especialidad=especialidad,
        )
        return self._repo.guardar(docente)
