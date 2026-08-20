import re
from dataclasses import dataclass

# Módulo-level constant to avoid dataclass field conflicts on frozen dataclasses
_PATRON_DOCUMENTO = re.compile(r"^[A-Za-z0-9\-]{3,30}$")


@dataclass(frozen=True)
class Email:
    valor: str

    def __post_init__(self):
        v = self.valor
        if "@" not in v:
            raise ValueError(f"Email inválido '{v}': debe contener '@'.")
        prefix, _, domain = v.partition("@")
        if not prefix:
            raise ValueError(f"Email inválido '{v}': el prefijo no puede estar vacío.")
        if "." not in domain:
            raise ValueError(
                f"Email inválido '{v}': el dominio debe contener al menos un punto."
            )


@dataclass(frozen=True)
class NumeroDocumento:
    valor: str

    def __post_init__(self):
        if not _PATRON_DOCUMENTO.match(self.valor):
            raise ValueError(
                f"NumeroDocumento inválido '{self.valor}': "
                "debe tener entre 3 y 30 caracteres alfanuméricos o guiones."
            )


@dataclass(frozen=True)
class Especialidad:
    valor: str

    def __post_init__(self):
        if not self.valor:
            raise ValueError("Especialidad no puede estar vacía.")
        if len(self.valor) > 100:
            raise ValueError(
                f"Especialidad '{self.valor[:20]}…' supera el límite de 100 caracteres."
            )
