"""Punto de arranque (raíz de composición): arma el hexágono con sus adaptadores.

Es el único módulo que conoce a la vez el hexágono y todos los adaptadores. Elige qué adaptador
se conecta a cada puerto: SQLite al repositorio, el reloj del sistema (o uno fijo, en las pruebas)
al reloj, y Flask al puerto de entrada.
"""
from pathlib import Path
import os

from avistamientos.adaptadores.primarios.http_flask import crear_aplicacion_flask
from avistamientos.adaptadores.secundarios.reloj_sistema import RelojDelSistema
from avistamientos.adaptadores.secundarios.repositorio_sqlite import RepositorioSQLite
from avistamientos.hexagono.puertos import GestionDeAvistamientos, Reloj
from avistamientos.hexagono.servicio import ServicioDeAvistamientos
from avistamientos.hexagono.validacion import ValidadorDeAvistamiento

RUTA_BD_POR_DEFECTO = str(Path(__file__).parent / 'avistamientos.db')


def construir_servicio(ruta_bd: str, reloj: Reloj = None) -> GestionDeAvistamientos:
    """Conecta los adaptadores secundarios a los puertos de salida y devuelve el puerto de entrada."""
    return ServicioDeAvistamientos(
        RepositorioSQLite(ruta_bd),
        ValidadorDeAvistamiento(reloj or RelojDelSistema()),
    )


def crear_app(config=None, reloj=None):
    configuracion = {'DATABASE': os.environ.get('DATABASE_PATH', RUTA_BD_POR_DEFECTO)}
    if config:
        configuracion.update(config)
    servicio = construir_servicio(configuracion['DATABASE'], reloj)
    return crear_aplicacion_flask(servicio, configuracion)


app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
