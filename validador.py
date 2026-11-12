"""Módulo puente TEMPORAL: la regla de negocio se movió a avistamientos/hexagono/validacion.py.

Se mantiene solo para que las pruebas sigan importando desde aquí mientras dura el refactor.
"""
from avistamientos.hexagono.errores import ErrorDeValidacion  # noqa: F401
from avistamientos.hexagono.validacion import (  # noqa: F401
    ESPECIE_MAX, ESPECIE_MIN, ValidadorDeAvistamiento)
