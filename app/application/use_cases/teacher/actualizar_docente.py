from dataclasses import replace

from app.application.ports.teacher_repository import DocenteRepository
from app.domain.entities.teacher import Docente
from app.domain.exceptions import ConflictoDeUnicidad, EntidadNoEncontrada


class ActualizarDocente:
    def __init__(self, repo: DocenteRepository):
        self._repo = repo

    def ejecutar(self, id: int, **campos) -> Docente:
        """Actualiza los campos indicados de un docente existente.

        Si ``campos`` está vacío la operación es un no-op y devuelve la entidad
        tal como está almacenada, sin emitir ninguna escritura.

        Args:
            id: Clave primaria del docente a actualizar.
            **campos: Campos a actualizar (``nombre``, ``email``,
                ``especialidad``, ``activo``). Los campos no presentes conservan
                su valor actual.

        Returns:
            La entidad ``Docente`` con los campos actualizados.

        Raises:
            EntidadNoEncontrada: Si no existe ningún docente con ese ``id``.
            ConflictoDeUnicidad: Si el nuevo ``email`` o la nueva
                ``especialidad`` ya pertenece a otro docente.
        """
        docente = self._repo.obtener_por_id(id)
        if docente is None:
            raise EntidadNoEncontrada("Docente", id)

        # No-op: return unchanged entity without any write
        if not campos:
            return docente

        # Validate email uniqueness if it is being updated
        nuevo_email = campos.get("email")
        if nuevo_email is not None and nuevo_email != docente.email:
            existente = self._repo.obtener_por_email(nuevo_email)
            if existente is not None:
                raise ConflictoDeUnicidad("email", nuevo_email)

        # Validate especialidad uniqueness if it is being updated
        nueva_especialidad = campos.get("especialidad")
        if nueva_especialidad is not None and nueva_especialidad != docente.especialidad:
            existentes = self._repo.obtener_por_especialidad(nueva_especialidad)
            if existentes:
                raise ConflictoDeUnicidad("especialidad", nueva_especialidad)

        # Apply field updates
        nombre = campos.get("nombre", docente.nombre)
        email = campos.get("email", docente.email)
        especialidad = campos.get("especialidad", docente.especialidad)
        activo = campos.get("activo", docente.activo)

        docente_actualizado = replace(
            docente,
            nombre=nombre,
            email=email,
            especialidad=especialidad,
            activo=activo,
        )
        return self._repo.guardar(docente_actualizado)
