from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Docente:
    nombre: str
    email: str
    especialidad: str
    id: int = 0
    activo: bool = True
    fecha_creacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
