from enum import Enum


class OrigenConsulta(str, Enum):
    """Quien genero la consulta registrada (HU-09, ADR-013). Solo `usuario` es demanda real;
    el resto son consultas sinteticas de pruebas y nunca cuentan como tal."""

    USUARIO = "usuario"
    CARGA = "carga"
    ARNES = "arnes"
    HUMO = "humo"
