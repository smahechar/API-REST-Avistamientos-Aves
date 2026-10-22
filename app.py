"""Capa HTTP: solo traduce peticiones a llamadas del servicio y errores a códigos."""
from pathlib import Path
import os

from flask import Flask, jsonify, request

from repositorio import RepositorioSQLite
from reloj import RelojDelSistema
from servicio import NoEncontrado, ServicioDeAvistamientos
from validador import ErrorDeValidacion, ValidadorDeAvistamiento


def crear_app(config=None, reloj=None):
    app = Flask(__name__)
    # Mostrar caracteres como á, ñ y ü en lugar de secuencias Unicode.
    app.json.ensure_ascii = False
    # JSON con saltos de línea y sangría para facilitar su lectura.
    app.json.compact = False
    app.config['DATABASE'] = os.environ.get('DATABASE_PATH', str(Path(__file__).parent / 'avistamientos.db'))
    if config:
        app.config.update(config)

    servicio = ServicioDeAvistamientos(
        RepositorioSQLite(app.config['DATABASE']),
        ValidadorDeAvistamiento(reloj or RelojDelSistema()),
    )

    @app.errorhandler(ErrorDeValidacion)
    def _validacion(error):
        return jsonify(error=str(error), campo=error.campo), 400

    @app.errorhandler(NoEncontrado)
    def _no_encontrado(_error):
        return jsonify(error='Avistamiento no encontrado.'), 404

    @app.get('/avistamientos')
    def listar():
        return jsonify(servicio.listar()), 200

    @app.get('/avistamientos/resumen')
    def resumen():
        return jsonify(servicio.resumen()), 200

    @app.get('/avistamientos/<int:identificador>')
    def consultar(identificador):
        return jsonify(servicio.consultar(identificador)), 200

    @app.post('/avistamientos')
    def crear():
        datos = request.get_json(silent=True)
        return jsonify(servicio.crear(datos)), 201

    @app.put('/avistamientos/<int:identificador>')
    def actualizar(identificador):
        datos = request.get_json(silent=True)
        return jsonify(servicio.actualizar(identificador, datos)), 200

    @app.delete('/avistamientos/<int:identificador>')
    def eliminar(identificador):
        servicio.eliminar(identificador)
        return '', 204

    return app


app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
