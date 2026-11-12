"""Errores del dominio. Los lanza el hexágono; cada adaptador primario decide cómo presentarlos
(el adaptador HTTP los traduce a 400 y 404)."""


class ErrorDeValidacion(Exception):
    """Un campo del avistamiento no cumple la regla. Indica cuál falló."""

    def __init__(self, campo: str, mensaje: str):
        super().__init__(f'{campo}: {mensaje}')
        self.campo = campo
        self.mensaje = mensaje


class NoEncontrado(Exception):
    """No existe un avistamiento con ese id."""
