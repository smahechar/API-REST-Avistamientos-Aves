"""Adaptador secundario: implementa el puerto Reloj con la fecha del sistema operativo."""
from datetime import date

from avistamientos.hexagono.puertos import Reloj


class RelojDelSistema(Reloj):
    """Implementación real: devuelve la fecha actual del sistema."""

    def hoy(self) -> date:
        return date.today()
