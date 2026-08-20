"""
Modelo ORM SQLAlchemy para la tabla 'estudiantes'.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    direccion: Mapped[str] = mapped_column(String(500), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Estudiante id={self.id} nombre={self.nombre!r} email={self.email!r}>"


class Docente(Base):
    __tablename__ = "docentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    especialidad: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Docente id={self.id} nombre={self.nombre!r} email={self.email!r} especialidad={self.especialidad!r}>"
