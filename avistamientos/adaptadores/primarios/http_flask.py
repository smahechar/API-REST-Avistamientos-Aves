"""Adaptador primario HTTP: traduce peticiones Flask a llamadas del puerto de entrada
y los errores del dominio a códigos de estado HTTP.

Es el único lugar del proyecto que conoce Flask. No contiene reglas de negocio ni SQL.
"""
from flask import Flask, jsonify, request

from avistamientos.hexagono.errores import ErrorDeValidacion, NoEncontrado
from avistamientos.hexagono.puertos import GestionDeAvistamientos


def crear_aplicacion_flask(gestion: GestionDeAvistamientos, config=None) -> Flask:
    app = Flask(__name__)
    # Mostrar caracteres como á, ñ y ü en lugar de secuencias Unicode.
    app.json.ensure_ascii = False
    # JSON con saltos de línea y sangría para facilitar su lectura.
    app.json.compact = False
    if config:
        app.config.update(config)

    @app.errorhandler(ErrorDeValidacion)
    def _validacion(error):
        return jsonify(error=str(error), campo=error.campo), 400

    @app.errorhandler(NoEncontrado)
    def _no_encontrado(_error):
        return jsonify(error='Avistamiento no encontrado.'), 404

    @app.get('/avistamientos')
    def listar():
        return jsonify(gestion.listar()), 200

    @app.get('/avistamientos/resumen')
    def resumen():
        return jsonify(gestion.resumen()), 200

    @app.get('/avistamientos/<int:identificador>')
    def consultar(identificador):
        return jsonify(gestion.consultar(identificador)), 200

    @app.post('/avistamientos')
    def crear():
        datos = request.get_json(silent=True)
        return jsonify(gestion.crear(datos)), 201

    @app.put('/avistamientos/<int:identificador>')
    def actualizar(identificador):
        datos = request.get_json(silent=True)
        return jsonify(gestion.actualizar(identificador, datos)), 200

    @app.delete('/avistamientos/<int:identificador>')
    def eliminar(identificador):
        gestion.eliminar(identificador)
        return '', 204

    return app
