"""Muestra reproducible de cómo responde la API (evidencia "antes" / "después" del refactor).

Ejecuta siempre la misma secuencia de peticiones contra una base SQLite temporal y un reloj
fijo (hoy = 2026-10-21), e imprime método, ruta, código y cuerpo de cada respuesta.
Si la salida antes y después del refactor es idéntica, la API responde igual.

Ejecutar desde la raíz del proyecto:  python herramientas/muestra_api.py
"""
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import crear_app  # noqa: E402


class _RelojFijo:
    def hoy(self):
        return date(2026, 10, 21)


VALIDO = {'especie': 'Colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana'}

PETICIONES = [
    ('GET', '/avistamientos', None),
    ('POST', '/avistamientos', VALIDO),
    ('POST', '/avistamientos', {**VALIDO, 'especie': '  Garza blanca  ', 'fecha': '2026-10-21'}),
    ('POST', '/avistamientos', {**VALIDO, 'especie': 'ab'}),
    ('POST', '/avistamientos', {**VALIDO, 'fecha': '2026-10-22'}),
    ('POST', '/avistamientos', {**VALIDO, 'fecha': '2026-02-30'}),
    ('POST', '/avistamientos', {'especie': 'Búho'}),
    ('POST', '/avistamientos', 'esto no es JSON'),
    ('GET', '/avistamientos', None),
    ('GET', '/avistamientos/1', None),
    ('GET', '/avistamientos/999', None),
    ('GET', '/avistamientos/resumen', None),
    ('PUT', '/avistamientos/1', {**VALIDO, 'especie': 'Garza blanca'}),
    ('PUT', '/avistamientos/1', {**VALIDO, 'observador': '   '}),
    ('PUT', '/avistamientos/999', {}),
    ('GET', '/avistamientos/resumen', None),
    ('DELETE', '/avistamientos/1', None),
    ('DELETE', '/avistamientos/1', None),
    ('GET', '/avistamientos', None),
]


def main():
    # UTF-8 también en Windows, para que tildes y eñes se guarden bien al redirigir a un archivo.
    sys.stdout.reconfigure(encoding='utf-8')
    with tempfile.TemporaryDirectory() as carpeta:
        app = crear_app({'TESTING': True, 'DATABASE': str(Path(carpeta) / 'muestra.db')},
                        reloj=_RelojFijo())
        cliente = app.test_client()
        for metodo, ruta, cuerpo in PETICIONES:
            if isinstance(cuerpo, str):
                respuesta = cliente.open(ruta, method=metodo, data=cuerpo,
                                         content_type='text/plain')
            else:
                respuesta = cliente.open(ruta, method=metodo, json=cuerpo)
            contenido = respuesta.get_json(silent=True)
            texto = json.dumps(contenido, ensure_ascii=False, sort_keys=True) if contenido is not None else '(sin cuerpo)'
            print(f'{metodo:6} {ruta:26} -> {respuesta.status_code}  {texto}')


if __name__ == '__main__':
    main()
