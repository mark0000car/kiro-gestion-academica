class EntidadNoEncontrada(Exception):
    """Lanzada cuando un caso de uso no encuentra la entidad solicitada."""

    def __init__(self, entidad: str, identificador):
        self.entidad = entidad
        self.identificador = identificador
        super().__init__(f"{entidad} con id={identificador!r} no encontrado.")


class ConflictoDeUnicidad(Exception):
    """Lanzada cuando se viola una restricción de unicidad."""

    def __init__(self, campo: str, valor: str = ""):
        self.campo = campo
        self.valor = valor
        super().__init__(f"Ya existe un registro con {campo}={valor!r}.")


class ValidacionDominio(Exception):
    """Lanzada cuando los datos de entrada violan una regla de negocio del dominio."""

    def __init__(self, campo: str, mensaje: str):
        self.campo = campo
        super().__init__(f"Validación fallida en '{campo}': {mensaje}")
