from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Estudiante:
    nombre: str
    direccion: str
    numero_documento: str
    email: str
    id: int = 0                        # 0 = no persistido aún
    activo: bool = True
    fecha_creacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
