"""Prueba de contrato: el FAKE (en memoria) y el repositorio REAL (SQLite) deben comportarse igual.

Si el fake se desviara del real, las pruebas unitarias del servicio dejarían de ser confiables.
Cada caso se ejecuta contra las dos implementaciones.
"""
import pytest

from repositorio import RepositorioSQLite
from tests.dobles import RepositorioEnMemoria

DATOS = {'especie': 'Colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana'}


@pytest.fixture(params=['memoria', 'sqlite'])
def repositorio(request, tmp_path):
    if request.param == 'memoria':
        return RepositorioEnMemoria()
    return RepositorioSQLite(str(tmp_path / 'contrato.db'))


def test_crear_asigna_ids_consecutivos_desde_1(repositorio):
    # Arrange / Act
    primero = repositorio.crear(DATOS)
    segundo = repositorio.crear(DATOS)
    # Assert
    assert (primero['id'], segundo['id']) == (1, 2)


def test_obtener_devuelve_none_si_no_existe(repositorio):
    # Arrange / Act / Assert
    assert repositorio.obtener(5) is None


def test_actualizar_devuelve_none_si_no_existe_y_el_registro_si_existe(repositorio):
    # Arrange
    repositorio.crear(DATOS)
    # Act / Assert
    assert repositorio.actualizar(99, DATOS) is None
    assert repositorio.actualizar(1, {**DATOS, 'especie': 'Garza'})['especie'] == 'Garza'


def test_eliminar_devuelve_true_si_existia_y_false_si_no(repositorio):
    # Arrange
    repositorio.crear(DATOS)
    # Act / Assert
    assert repositorio.eliminar(1) is True
    assert repositorio.eliminar(1) is False


def test_listar_y_resumen_coinciden_entre_implementaciones(repositorio):
    # Arrange
    repositorio.crear({**DATOS, 'especie': 'Garza'})
    repositorio.crear(DATOS)
    repositorio.crear(DATOS)
    # Act / Assert
    assert [r['id'] for r in repositorio.listar()] == [1, 2, 3]
    assert repositorio.resumen() == [{'especie': 'Colibrí', 'cantidad': 2}, {'especie': 'Garza', 'cantidad': 1}]
