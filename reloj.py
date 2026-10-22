"""Abstracción del reloj. Permite probar reglas que dependen de "hoy"."""
from datetime import date


class RelojDelSistema:
    """Implementación real: devuelve la fecha actual del sistema."""

    def hoy(self) -> date:
        return date.today()
