"""Pruebas unitarias de ValidadorDeAvistamiento (sin Flask, sin base de datos).

Técnicas: partición de equivalencia y valores límite (ver docs/justificacion-pruebas.md, sección 2).
Doble: RelojFijo (stub) fija "hoy" en 2026-10-21.
"""
from datetime import date

import pytest

from tests.dobles import RelojFijo
from validador import ErrorDeValidacion, ValidadorDeAvistamiento

HOY = date(2026, 10, 21)


@pytest.fixture
def validador():
    return ValidadorDeAvistamiento(RelojFijo(HOY))


def datos_validos(**cambios):
    return {'especie': 'Colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana', **cambios}


# ---------- Especie: límites (3..50) ----------

def test_especie_de_2_caracteres_se_rechaza_por_corta(validador):
    # Arrange
    datos = datos_validos(especie='ab')
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'especie'


def test_especie_de_3_caracteres_se_acepta_por_ser_el_limite_inferior(validador):
    # Arrange
    datos = datos_validos(especie='abc')
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado['especie'] == 'abc'


def test_especie_de_50_caracteres_se_acepta_por_ser_el_limite_superior(validador):
    # Arrange
    datos = datos_validos(especie='a' * 50)
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert len(resultado['especie']) == 50


def test_especie_de_51_caracteres_se_rechaza_por_larga(validador):
    # Arrange
    datos = datos_validos(especie='a' * 51)
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'especie'


def test_especie_representativa_de_longitud_media_se_acepta(validador):
    # Arrange
    datos = datos_validos(especie='Tángara multicolor')
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado['especie'] == 'Tángara multicolor'


def test_especie_con_espacios_alrededor_se_mide_sin_ellos(validador):
    # Arrange: 2 letras + espacios = 6 caracteres crudos, pero 2 reales
    datos = datos_validos(especie='  ab  ')
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'especie'


@pytest.mark.parametrize('valor', [None, '', '   ', 123, ['garza']],
                         ids=['nulo', 'vacia', 'solo_espacios', 'numero', 'lista'])
def test_especie_vacia_o_que_no_es_texto_se_rechaza(validador, valor):
    # Arrange
    datos = datos_validos(especie=valor)
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'especie'


# ---------- Fecha: límite "hoy" ----------

def test_fecha_de_hoy_se_acepta_por_ser_el_limite_superior(validador):
    # Arrange
    datos = datos_validos(fecha='2026-10-21')
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado['fecha'] == '2026-10-21'


def test_fecha_de_manana_se_rechaza_por_ser_posterior_a_hoy(validador):
    # Arrange
    datos = datos_validos(fecha='2026-10-22')
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'fecha'
    assert 'posterior' in error.value.mensaje


def test_fecha_de_ayer_se_acepta(validador):
    # Arrange
    datos = datos_validos(fecha='2026-10-20')
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado['fecha'] == '2026-10-20'


def test_fecha_de_un_anio_futuro_se_rechaza_aunque_el_mes_y_dia_sean_anteriores(validador):
    # Arrange: 2027-01-01 es posterior a hoy aunque 01-01 < 10-21 (compara la fecha completa)
    datos = datos_validos(fecha='2027-01-01')
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'fecha'


def test_fecha_bisiesta_real_se_acepta(validador):
    # Arrange
    datos = datos_validos(fecha='2024-02-29')
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado['fecha'] == '2024-02-29'


# ---------- Fecha: formato y calendario (clases inválidas) ----------

@pytest.mark.parametrize('texto', ['29-09-2026', '2026/09/29', '2026-9-29', '20260929', '2026-09-29T10:00', 'ayer'],
                         ids=['dia_primero', 'barras', 'sin_ceros', 'sin_guiones', 'con_hora', 'texto'])
def test_fecha_con_formato_distinto_de_AAAA_MM_DD_se_rechaza(validador, texto):
    # Arrange
    datos = datos_validos(fecha=texto)
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'fecha'
    assert 'AAAA-MM-DD' in error.value.mensaje


@pytest.mark.parametrize('texto', ['2026-02-30', '2025-02-29', '2026-13-01', '2026-00-10'],
                         ids=['30_febrero', '29_feb_no_bisiesto', 'mes_13', 'mes_0'])
def test_fecha_con_formato_correcto_pero_inexistente_se_rechaza(validador, texto):
    # Arrange
    datos = datos_validos(fecha=texto)
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'fecha'


@pytest.mark.parametrize('valor', [None, '', '  ', 20260929],
                         ids=['nula', 'vacia', 'solo_espacios', 'numero'])
def test_fecha_vacia_o_que_no_es_texto_se_rechaza(validador, valor):
    # Arrange
    datos = datos_validos(fecha=valor)
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == 'fecha'


# ---------- Lugar y observador ----------

@pytest.mark.parametrize('campo', ['lugar', 'observador'])
@pytest.mark.parametrize('valor', [None, '', '   '], ids=['nulo', 'vacio', 'solo_espacios'])
def test_lugar_u_observador_vacio_se_rechaza_indicando_el_campo(validador, campo, valor):
    # Arrange
    datos = datos_validos(**{campo: valor})
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == campo


@pytest.mark.parametrize('campo', ['especie', 'fecha', 'lugar', 'observador'])
def test_campo_ausente_se_rechaza_indicando_cual_falta(validador, campo):
    # Arrange
    datos = datos_validos()
    del datos[campo]
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(datos)
    # Assert
    assert error.value.campo == campo
    assert campo in str(error.value)


# ---------- Cuerpo y resultado ----------

@pytest.mark.parametrize('cuerpo', [None, [], 'texto', 42], ids=['nulo', 'lista', 'texto', 'numero'])
def test_cuerpo_que_no_es_un_objeto_se_rechaza(validador, cuerpo):
    # Arrange: el cuerpo ya viene en `cuerpo`
    # Act
    with pytest.raises(ErrorDeValidacion) as error:
        validador.validar(cuerpo)
    # Assert
    assert error.value.campo == 'cuerpo'


def test_avistamiento_valido_se_devuelve_normalizado_sin_espacios_en_los_extremos(validador):
    # Arrange
    datos = {'especie': '  Garza  ', 'lugar': ' Chía ', 'fecha': ' 2026-09-30 ', 'observador': ' Ana '}
    # Act
    resultado = validador.validar(datos)
    # Assert
    assert resultado == {'especie': 'Garza', 'lugar': 'Chía', 'fecha': '2026-09-30', 'observador': 'Ana'}


def test_el_validador_usa_el_reloj_inyectado_no_el_del_sistema():
    # Arrange: dos relojes distintos, misma fecha de entrada
    datos = datos_validos(fecha='2026-06-15')
    antes = ValidadorDeAvistamiento(RelojFijo(date(2026, 6, 14)))
    despues = ValidadorDeAvistamiento(RelojFijo(date(2026, 6, 15)))
    # Act / Assert
    with pytest.raises(ErrorDeValidacion):
        antes.validar(datos)
    assert despues.validar(datos)['fecha'] == '2026-06-15'
