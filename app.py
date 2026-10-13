from datetime import date
from pathlib import Path
import os
import sqlite3

from flask import Flask, jsonify, request

CAMPOS = ('especie', 'lugar', 'fecha', 'observador')


def crear_app(config=None):
    app = Flask(__name__)
    # Mostrar caracteres como á, ñ y ü en lugar de secuencias Unicode.
    app.json.ensure_ascii = False
    # JSON con saltos de línea y sangría para facilitar su lectura.
    app.json.compact = False
    app.config['DATABASE'] = os.environ.get('DATABASE_PATH', str(Path(__file__).parent / 'avistamientos.db'))
    if config:
        app.config.update(config)

    def conectar():
        conexion = sqlite3.connect(app.config['DATABASE'])
        conexion.row_factory = sqlite3.Row
        return conexion

    with conectar() as conexion:
        conexion.execute('''CREATE TABLE IF NOT EXISTS avistamientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            especie TEXT NOT NULL,
            lugar TEXT NOT NULL,
            fecha TEXT NOT NULL,
            observador TEXT NOT NULL
        )''')

    def validar(datos):
        if not isinstance(datos, dict):
            return 'Se requiere un objeto JSON.'
        if any(not isinstance(datos.get(c), str) or not datos[c].strip() for c in CAMPOS):
            return 'Los campos especie, lugar, fecha y observador son obligatorios y deben ser textos no vacíos.'
        try:
            if date.fromisoformat(datos['fecha']).isoformat() != datos['fecha']:
                raise ValueError
        except ValueError:
            return 'La fecha debe ser válida y tener formato AAAA-MM-DD.'
        return None

    @app.get('/avistamientos')
    def listar():
        with conectar() as conexion:
            filas = conexion.execute('SELECT * FROM avistamientos ORDER BY id').fetchall()
        return jsonify([dict(f) for f in filas]), 200

    @app.get('/avistamientos/resumen')
    def resumen():
        with conectar() as conexion:
            filas = conexion.execute('SELECT especie, COUNT(*) AS cantidad FROM avistamientos GROUP BY especie ORDER BY especie').fetchall()
        return jsonify([dict(f) for f in filas]), 200

    @app.get('/avistamientos/<int:identificador>')
    def consultar(identificador):
        with conectar() as conexion:
            fila = conexion.execute('SELECT * FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
        return (jsonify(dict(fila)), 200) if fila else (jsonify(error='Avistamiento no encontrado.'), 404)

    @app.post('/avistamientos')
    def crear():
        datos = request.get_json(silent=True)
        error = validar(datos)
        if error:
            return jsonify(error=error), 400
        valores = [datos[c].strip() for c in CAMPOS]
        with conectar() as conexion:
            cursor = conexion.execute('INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)', valores)
            identificador = cursor.lastrowid
            fila = conexion.execute('SELECT * FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
        return jsonify(dict(fila)), 201

    @app.put('/avistamientos/<int:identificador>')
    def actualizar(identificador):
        with conectar() as conexion:
            existe = conexion.execute('SELECT id FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
            if not existe:
                return jsonify(error='Avistamiento no encontrado.'), 404
            datos = request.get_json(silent=True)
            error = validar(datos)
            if error:
                return jsonify(error=error), 400
            valores = [datos[c].strip() for c in CAMPOS]
            conexion.execute('UPDATE avistamientos SET especie=?, lugar=?, fecha=?, observador=? WHERE id=?', (*valores, identificador))
            fila = conexion.execute('SELECT * FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
        return jsonify(dict(fila)), 200

    @app.delete('/avistamientos/<int:identificador>')
    def eliminar(identificador):
        with conectar() as conexion:
            cursor = conexion.execute('DELETE FROM avistamientos WHERE id = ?', (identificador,))
            if cursor.rowcount == 0:
                return jsonify(error='Avistamiento no encontrado.'), 404
        return '', 204

    return app


app = crear_app()

if __name__ == '__main__':
    app.run(debug=True)
