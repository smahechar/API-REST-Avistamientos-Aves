"""Pruebas unitarias de ServicioDeAvistamientos con dobles del repositorio.

- RepositorioEnMemoria (fake): para verificar el ESTADO resultante.
- Mock de unittest.mock: para verificar que NO se persiste nada cuando hay un error (COMPORTAMIENTO).
- RelojFijo (stub): fija "hoy".
"""
from datetime import date
from unittest.mock import Mock

import pytest

from servicio import NoEncontrado, ServicioDeAvistamientos
from tests.dobles import RelojFijo, RepositorioEnMemoria
from validador import ErrorDeValidacion, ValidadorDeAvistamiento

VALIDO = {'especie': 'Colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana'}


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(date(2026, 10, 21)))


@pytest.fixture
def servicio(validador):
    return ServicioDeAvistamientos(RepositorioEnMemoria(), validador)


def test_crear_con_datos_validos_devuelve_el_registro_con_id_y_queda_consultable(servicio):
    # Arrange: servicio con repositorio vacío
    # Act
    creado = servicio.crear(VALIDO)
    # Assert
    assert creado == {'id': 1, **VALIDO}
    assert servicio.consultar(1) == creado


def test_crear_guarda_los_datos_normalizados(servicio):
    # Arrange
    datos = {**VALIDO, 'especie': '  Garza  '}
    # Act
    creado = servicio.crear(datos)
    # Assert
    assert creado['especie'] == 'Garza'


def test_crear_con_datos_invalidos_lanza_error_y_no_llama_al_repositorio(validador):
    # Arrange
    repositorio = Mock()
    servicio = ServicioDeAvistamientos(repositorio, validador)
    # Act
    with pytest.raises(ErrorDeValidacion):
        servicio.crear({**VALIDO, 'especie': 'ab'})
    # Assert
    repositorio.crear.assert_not_called()


def test_crear_con_datos_validos_pide_al_repositorio_guardar_exactamente_una_vez(validador):
    # Arrange
    repositorio = Mock()
    repositorio.crear.return_value = {'id': 7, **VALIDO}
    servicio = ServicioDeAvistamientos(repositorio, validador)
    # Act
    servicio.crear(VALIDO)
    # Assert
    repositorio.crear.assert_called_once_with(VALIDO)


def test_consultar_un_id_inexistente_lanza_no_encontrado(servicio):
    # Arrange: repositorio vacío
    # Act / Assert
    with pytest.raises(NoEncontrado):
        servicio.consultar(999)


def test_actualizar_un_id_inexistente_lanza_no_encontrado_aunque_los_datos_sean_invalidos(servicio):
    # Arrange: datos inválidos a propósito; el 404 tiene prioridad sobre el 400
    # Act / Assert
    with pytest.raises(NoEncontrado):
        servicio.actualizar(999, {})


def test_actualizar_con_datos_invalidos_no_modifica_el_registro_existente(servicio):
    # Arrange
    servicio.crear(VALIDO)
    # Act
    with pytest.raises(ErrorDeValidacion):
        servicio.actualizar(1, {**VALIDO, 'especie': 'x' * 51})
    # Assert
    assert servicio.consultar(1)['especie'] == 'Colibrí'


def test_actualizar_con_datos_validos_reemplaza_el_registro(servicio):
    # Arrange
    servicio.crear(VALIDO)
    # Act
    actualizado = servicio.actualizar(1, {**VALIDO, 'especie': 'Garza'})
    # Assert
    assert actualizado == {'id': 1, **VALIDO, 'especie': 'Garza'}
    assert servicio.consultar(1)['especie'] == 'Garza'


def test_eliminar_un_registro_existente_lo_hace_inconsultable(servicio):
    # Arrange
    servicio.crear(VALIDO)
    # Act
    servicio.eliminar(1)
    # Assert
    with pytest.raises(NoEncontrado):
        servicio.consultar(1)


def test_eliminar_un_id_inexistente_lanza_no_encontrado(servicio):
    # Arrange: repositorio vacío
    # Act / Assert
    with pytest.raises(NoEncontrado):
        servicio.eliminar(1)


def test_resumen_cuenta_avistamientos_por_especie(servicio):
    # Arrange
    servicio.crear(VALIDO)
    servicio.crear(VALIDO)
    servicio.crear({**VALIDO, 'especie': 'Garza'})
    # Act
    resumen = servicio.resumen()
    # Assert
    assert resumen == [{'especie': 'Colibrí', 'cantidad': 2}, {'especie': 'Garza', 'cantidad': 1}]
