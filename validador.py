"""Regla de negocio: validez de un avistamiento.

Lógica pura: no conoce Flask, ni SQLite, ni el reloj del sistema.
La fecha de "hoy" se obtiene de un reloj inyectado.
"""
import re
from datetime import date

ESPECIE_MIN = 3
ESPECIE_MAX = 50
_FORMATO_FECHA = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}')


class ErrorDeValidacion(Exception):
    """Un campo del avistamiento no cumple la regla. Indica cuál falló."""

    def __init__(self, campo: str, mensaje: str):
        super().__init__(f'{campo}: {mensaje}')
        self.campo = campo
        self.mensaje = mensaje


class ValidadorDeAvistamiento:
    def __init__(self, reloj):
        self._reloj = reloj

    def validar(self, datos) -> dict:
        """Devuelve los datos normalizados (sin espacios en los extremos).

        Lanza ErrorDeValidacion con el campo que falló si no son válidos.
        """
        if not isinstance(datos, dict):
            raise ErrorDeValidacion('cuerpo', 'se requiere un objeto JSON.')

        limpios = {}
        for campo in ('especie', 'fecha', 'lugar', 'observador'):
            valor = datos.get(campo)
            if not isinstance(valor, str) or not valor.strip():
                raise ErrorDeValidacion(campo, 'es obligatorio y debe ser un texto no vacío.')
            limpios[campo] = valor.strip()

        self._validar_especie(limpios['especie'])
        self._validar_fecha(limpios['fecha'])
        return limpios

    @staticmethod
    def _validar_especie(especie: str) -> None:
        if not ESPECIE_MIN <= len(especie) <= ESPECIE_MAX:
            raise ErrorDeValidacion(
                'especie', f'debe tener entre {ESPECIE_MIN} y {ESPECIE_MAX} caracteres.')

    def _validar_fecha(self, texto: str) -> None:
        if not _FORMATO_FECHA.fullmatch(texto):
            raise ErrorDeValidacion('fecha', 'debe tener formato AAAA-MM-DD.')
        try:
            fecha = date(int(texto[:4]), int(texto[5:7]), int(texto[8:10]))
        except ValueError:
            raise ErrorDeValidacion('fecha', 'no es una fecha real del calendario.') from None
        if fecha > self._reloj.hoy():
            raise ErrorDeValidacion('fecha', 'no puede ser posterior a hoy.')
