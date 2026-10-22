"""Acceso a datos: único lugar que conoce SQLite."""
import sqlite3
from contextlib import contextmanager

_CAMPOS = ('especie', 'lugar', 'fecha', 'observador')


class RepositorioSQLite:
    def __init__(self, ruta: str):
        self._ruta = ruta
        with self._conectar() as conexion:
            conexion.execute('''CREATE TABLE IF NOT EXISTS avistamientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                lugar TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observador TEXT NOT NULL
            )''')

    @contextmanager
    def _conectar(self):
        """Abre una conexión, confirma (o revierte) la transacción y SIEMPRE la cierra.

        `with sqlite3.connect(...)` solo confirma/revierte; no cierra la conexión.
        """
        conexion = sqlite3.connect(self._ruta)
        conexion.row_factory = sqlite3.Row
        try:
            with conexion:
                yield conexion
        finally:
            conexion.close()

    def listar(self) -> list:
        with self._conectar() as conexion:
            filas = conexion.execute('SELECT * FROM avistamientos ORDER BY id').fetchall()
        return [dict(f) for f in filas]

    def resumen(self) -> list:
        with self._conectar() as conexion:
            filas = conexion.execute(
                'SELECT especie, COUNT(*) AS cantidad FROM avistamientos '
                'GROUP BY especie ORDER BY especie').fetchall()
        return [dict(f) for f in filas]

    def obtener(self, identificador: int):
        with self._conectar() as conexion:
            fila = conexion.execute(
                'SELECT * FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
        return dict(fila) if fila else None

    def crear(self, datos: dict) -> dict:
        valores = [datos[c] for c in _CAMPOS]
        with self._conectar() as conexion:
            cursor = conexion.execute(
                'INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)',
                valores)
            fila = conexion.execute(
                'SELECT * FROM avistamientos WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return dict(fila)

    def actualizar(self, identificador: int, datos: dict):
        valores = [datos[c] for c in _CAMPOS]
        with self._conectar() as conexion:
            cursor = conexion.execute(
                'UPDATE avistamientos SET especie=?, lugar=?, fecha=?, observador=? WHERE id=?',
                (*valores, identificador))
            if cursor.rowcount == 0:
                return None
            fila = conexion.execute(
                'SELECT * FROM avistamientos WHERE id = ?', (identificador,)).fetchone()
        return dict(fila)

    def eliminar(self, identificador: int) -> bool:
        with self._conectar() as conexion:
            cursor = conexion.execute('DELETE FROM avistamientos WHERE id = ?', (identificador,))
        return cursor.rowcount > 0
