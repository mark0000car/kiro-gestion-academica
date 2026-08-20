from app.application.ports.student_repository import EstudianteRepository
from app.domain.entities.student import Estudiante
from app.domain.exceptions import ConflictoDeUnicidad


class CrearEstudiante:
    """Caso de uso: crear un nuevo estudiante.

    Verifica que no exista otro estudiante con el mismo email o número de
    documento antes de persistir la entidad nueva.
    """

    def __init__(self, repo: EstudianteRepository):
        self._repo = repo

    def ejecutar(
        self,
        nombre: str,
        direccion: str,
        numero_documento: str,
        email: str,
    ) -> Estudiante:
        """Crea y persiste un nuevo estudiante.

        Parámetros:
            nombre: Nombre completo del estudiante.
            direccion: Dirección postal del estudiante.
            numero_documento: Número de documento de identidad.
            email: Dirección de correo electrónico.

        Devuelve:
            La entidad ``Estudiante`` persistida con su ``id`` asignado.

        Lanza:
            ConflictoDeUnicidad: si ya existe un estudiante con el mismo
                ``email`` o ``numero_documento``.
        """
        if self._repo.obtener_por_email(email):
            raise ConflictoDeUnicidad("email", email)
        if self._repo.obtener_por_documento(numero_documento):
            raise ConflictoDeUnicidad("numero_documento", numero_documento)
        estudiante = Estudiante(
            nombre=nombre,
            direccion=direccion,
            numero_documento=numero_documento,
            email=email,
        )
        return self._repo.guardar(estudiante)
