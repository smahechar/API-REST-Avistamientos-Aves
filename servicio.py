"""Módulo puente TEMPORAL: los casos de uso se movieron a avistamientos/hexagono/servicio.py.

Se mantiene solo para que las pruebas sigan importando desde aquí mientras dura el refactor.
"""
from avistamientos.hexagono.errores import NoEncontrado  # noqa: F401
from avistamientos.hexagono.servicio import ServicioDeAvistamientos  # noqa: F401
