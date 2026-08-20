from dataclasses import replace

from app.application.ports.student_repository import EstudianteRepository
from app.domain.entities.student import Estudiante
from app.domain.exceptions import ConflictoDeUnicidad, EntidadNoEncontrada


class ActualizarEstudiante:
    """Caso de uso: actualizar campos de un estudiante existente."""

    def __init__(self, repo: EstudianteRepository):
        self._repo = repo

    def ejecutar(self, id: int, **campos) -> Estudiante:
        """Actualiza uno o más campos del estudiante identificado por ``id``.

        Si ``campos`` está vacío se devuelve la entidad tal como está, sin
        realizar ninguna escritura en el repositorio.

        Parámetros:
            id: Identificador del estudiante a actualizar.
            **campos: Campos a modificar (``nombre``, ``direccion``,
                ``numero_documento``, ``email``, ``activo``).

        Devuelve:
            La entidad ``Estudiante`` con los valores actualizados.

        Lanza:
            EntidadNoEncontrada: si no existe ningún estudiante con ese ``id``.
            ConflictoDeUnicidad: si el nuevo ``email`` o ``numero_documento``
                ya pertenece a otro estudiante.
        """
        estudiante = self._repo.obtener_por_id(id)
        if estudiante is None:
            raise EntidadNoEncontrada("Estudiante", id)

        # No-op when no fields are provided
        if not campos:
            return estudiante

        # Uniqueness check for email (only if it actually changes)
        nuevo_email = campos.get("email")
        if nuevo_email is not None and nuevo_email != estudiante.email:
            existente = self._repo.obtener_por_email(nuevo_email)
            if existente is not None:
                raise ConflictoDeUnicidad("email", nuevo_email)

        # Uniqueness check for numero_documento (only if it actually changes)
        nuevo_documento = campos.get("numero_documento")
        if nuevo_documento is not None and nuevo_documento != estudiante.numero_documento:
            existente = self._repo.obtener_por_documento(nuevo_documento)
            if existente is not None:
                raise ConflictoDeUnicidad("numero_documento", nuevo_documento)

        actualizado = replace(estudiante, **campos)
        return self._repo.guardar(actualizado)
