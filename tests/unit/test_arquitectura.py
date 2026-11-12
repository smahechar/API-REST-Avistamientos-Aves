"""Prueba de arquitectura: verifica la dirección de las dependencias del hexágono.

Cockburn (2005): el código de adentro no debe filtrarse hacia afuera ni depender de él.
Se revisan los import de cada archivo (con ast, sin ejecutarlo).
"""
import ast
from pathlib import Path

import pytest

PAQUETE = Path(__file__).resolve().parents[2] / 'avistamientos'
TECNOLOGIAS = ('flask', 'sqlite3', 'werkzeug')


def modulos_importados(archivo: Path) -> set:
    arbol = ast.parse(archivo.read_text(encoding='utf-8'))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    return nombres


def archivos_de(carpeta: str) -> list:
    return sorted((PAQUETE / carpeta).rglob('*.py'))


@pytest.mark.parametrize('archivo', archivos_de('hexagono'), ids=lambda a: a.name)
def test_el_hexagono_no_importa_tecnologias_ni_adaptadores(archivo):
    # Arrange / Act
    importados = modulos_importados(archivo)
    # Assert
    prohibidos = {m for m in importados
                  if m.split('.')[0] in TECNOLOGIAS or m.startswith('avistamientos.adaptadores')
                  or m == 'app'}
    assert prohibidos == set()


@pytest.mark.parametrize('lado, otro_lado', [('primarios', 'secundarios'), ('secundarios', 'primarios')])
def test_un_lado_de_adaptadores_no_conoce_al_otro(lado, otro_lado):
    # Arrange
    archivos = archivos_de(f'adaptadores/{lado}')
    # Act
    importados = set().union(*(modulos_importados(a) for a in archivos))
    # Assert
    assert not any(m.startswith(f'avistamientos.adaptadores.{otro_lado}') for m in importados)
