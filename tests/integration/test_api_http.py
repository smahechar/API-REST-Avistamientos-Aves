"""Pruebas de integración: la API completa por HTTP (rutas + servicio + validador + SQLite real).

Independencia: cada prueba recibe una base SQLite NUEVA en un directorio temporal (fixture `cliente`)
y crea sus propios datos. Ninguna depende del orden de ejecución.
El reloj es un stub fijo (2026-10-21), así los resultados no cambian con el día en que se corran.
"""
from datetime import date

import pytest

from app import crear_app
from tests.dobles import RelojFijo

VALIDO = {'especie': 'Colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana'}


@pytest.fixture
def cliente(tmp_path):
    app = crear_app({'TESTING': True, 'DATABASE': str(tmp_path / 'pruebas.db')},
                    reloj=RelojFijo(date(2026, 10, 21)))
    return app.test_client()


def crear(cliente, **cambios):
    """Prepara datos: crea un avistamiento por la propia API y devuelve el cuerpo."""
    respuesta = cliente.post('/avistamientos', json={**VALIDO, **cambios})
    assert respuesta.status_code == 201
    return respuesta.json


# ---------- GET /avistamientos ----------

def test_get_lista_devuelve_200_y_arreglo_vacio_cuando_no_hay_datos(cliente):
    # Arrange: base vacía
    # Act
    respuesta = cliente.get('/avistamientos')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == []


def test_get_lista_devuelve_200_con_todos_los_registros_en_orden_de_id(cliente):
    # Arrange
    a = crear(cliente, especie='Colibrí')
    b = crear(cliente, especie='Garza blanca')
    # Act
    respuesta = cliente.get('/avistamientos')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == [a, b]


# ---------- GET /avistamientos/<id> ----------

def test_get_por_id_devuelve_200_con_el_registro_completo(cliente):
    # Arrange
    creado = crear(cliente)
    # Act
    respuesta = cliente.get(f'/avistamientos/{creado["id"]}')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == {'id': creado['id'], **VALIDO}


def test_get_por_id_inexistente_devuelve_404_con_mensaje_de_error(cliente):
    # Arrange: base vacía
    # Act
    respuesta = cliente.get('/avistamientos/999')
    # Assert
    assert respuesta.status_code == 404
    assert respuesta.json == {'error': 'Avistamiento no encontrado.'}


# ---------- POST /avistamientos ----------

def test_post_valido_devuelve_201_con_el_cuerpo_y_queda_consultable_por_get(cliente):
    # Arrange
    datos = {**VALIDO, 'especie': 'Garza'}
    # Act
    respuesta = cliente.post('/avistamientos', json=datos)
    # Assert: respuesta y efecto
    assert respuesta.status_code == 201
    assert respuesta.json == {'id': 1, **datos}
    assert cliente.get('/avistamientos/1').json == respuesta.json


def test_post_guarda_los_textos_sin_espacios_en_los_extremos(cliente):
    # Arrange
    datos = {**VALIDO, 'especie': '  Garza  ', 'lugar': ' Chía '}
    # Act
    respuesta = cliente.post('/avistamientos', json=datos)
    # Assert
    assert respuesta.json['especie'] == 'Garza'
    assert cliente.get('/avistamientos/1').json['lugar'] == 'Chía'


@pytest.mark.parametrize('campo, valor', [
    ('especie', 'ab'),
    ('especie', 'a' * 51),
    ('fecha', '2026-10-22'),      # mañana (reloj fijo)
    ('fecha', '29-09-2026'),
    ('fecha', '2026-02-30'),
    ('lugar', ''),
    ('observador', '   '),
], ids=['especie_2', 'especie_51', 'fecha_manana', 'fecha_formato', 'fecha_inexistente',
        'lugar_vacio', 'observador_blanco'])
def test_post_invalido_devuelve_400_indica_el_campo_y_no_guarda_nada(cliente, campo, valor):
    # Arrange
    datos = {**VALIDO, campo: valor}
    # Act
    respuesta = cliente.post('/avistamientos', json=datos)
    # Assert: respuesta y efecto (nada persistido)
    assert respuesta.status_code == 400
    assert respuesta.json['campo'] == campo
    assert campo in respuesta.json['error']
    assert cliente.get('/avistamientos').json == []


def test_post_con_fecha_de_hoy_devuelve_201_por_ser_el_limite_permitido(cliente):
    # Arrange
    datos = {**VALIDO, 'fecha': '2026-10-21'}
    # Act
    respuesta = cliente.post('/avistamientos', json=datos)
    # Assert
    assert respuesta.status_code == 201


def test_post_con_cuerpo_que_no_es_json_devuelve_400(cliente):
    # Arrange: texto plano en vez de JSON
    # Act
    respuesta = cliente.post('/avistamientos', data='no soy json', content_type='text/plain')
    # Assert
    assert respuesta.status_code == 400
    assert respuesta.json['campo'] == 'cuerpo'


# ---------- PUT /avistamientos/<id> ----------

def test_put_valido_devuelve_200_con_el_registro_actualizado_y_get_lo_confirma(cliente):
    # Arrange
    creado = crear(cliente)
    nuevos = {**VALIDO, 'especie': 'Garza', 'lugar': 'Chía', 'fecha': '2026-09-30'}
    # Act
    respuesta = cliente.put(f'/avistamientos/{creado["id"]}', json=nuevos)
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == {'id': creado['id'], **nuevos}
    assert cliente.get(f'/avistamientos/{creado["id"]}').json == respuesta.json


def test_put_invalido_devuelve_400_y_el_registro_queda_intacto(cliente):
    # Arrange
    creado = crear(cliente)
    # Act
    respuesta = cliente.put(f'/avistamientos/{creado["id"]}', json={**VALIDO, 'fecha': '2026-10-22'})
    # Assert
    assert respuesta.status_code == 400
    assert respuesta.json['campo'] == 'fecha'
    assert cliente.get(f'/avistamientos/{creado["id"]}').json == creado


def test_put_a_id_inexistente_devuelve_404(cliente):
    # Arrange: base vacía
    # Act
    respuesta = cliente.put('/avistamientos/999', json=VALIDO)
    # Assert
    assert respuesta.status_code == 404
    assert respuesta.json == {'error': 'Avistamiento no encontrado.'}


def test_put_a_id_inexistente_con_cuerpo_invalido_devuelve_404_y_no_400(cliente):
    # Arrange: orden de precedencia: existencia antes que validez
    # Act
    respuesta = cliente.put('/avistamientos/999', json={})
    # Assert
    assert respuesta.status_code == 404


def test_put_no_modifica_los_otros_registros(cliente):
    # Arrange
    a = crear(cliente, especie='Colibrí')
    b = crear(cliente, especie='Garza')
    # Act
    cliente.put(f'/avistamientos/{a["id"]}', json={**VALIDO, 'especie': 'Turpial'})
    # Assert
    assert cliente.get(f'/avistamientos/{b["id"]}').json == b


# ---------- DELETE /avistamientos/<id> ----------

def test_delete_existente_devuelve_204_sin_cuerpo_y_despues_get_devuelve_404(cliente):
    # Arrange
    creado = crear(cliente)
    # Act
    respuesta = cliente.delete(f'/avistamientos/{creado["id"]}')
    # Assert
    assert respuesta.status_code == 204
    assert respuesta.data == b''
    assert cliente.get(f'/avistamientos/{creado["id"]}').status_code == 404
    assert cliente.get('/avistamientos').json == []


def test_delete_inexistente_devuelve_404(cliente):
    # Arrange: base vacía
    # Act
    respuesta = cliente.delete('/avistamientos/999')
    # Assert
    assert respuesta.status_code == 404
    assert respuesta.json == {'error': 'Avistamiento no encontrado.'}


def test_delete_dos_veces_el_mismo_id_responde_204_y_luego_404(cliente):
    # Arrange
    creado = crear(cliente)
    # Act
    primera = cliente.delete(f'/avistamientos/{creado["id"]}')
    segunda = cliente.delete(f'/avistamientos/{creado["id"]}')
    # Assert
    assert (primera.status_code, segunda.status_code) == (204, 404)


def test_delete_solo_elimina_el_registro_indicado(cliente):
    # Arrange
    a = crear(cliente)
    b = crear(cliente, especie='Garza')
    # Act
    cliente.delete(f'/avistamientos/{a["id"]}')
    # Assert
    assert cliente.get('/avistamientos').json == [b]


# ---------- GET /avistamientos/resumen ----------

def test_get_resumen_devuelve_200_y_arreglo_vacio_sin_datos(cliente):
    # Arrange: base vacía
    # Act
    respuesta = cliente.get('/avistamientos/resumen')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == []


def test_get_resumen_agrupa_y_cuenta_por_especie_ordenado_alfabeticamente(cliente):
    # Arrange
    crear(cliente, especie='Garza')
    crear(cliente, especie='Colibrí')
    crear(cliente, especie='Colibrí')
    # Act
    respuesta = cliente.get('/avistamientos/resumen')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == [{'especie': 'Colibrí', 'cantidad': 2}, {'especie': 'Garza', 'cantidad': 1}]


def test_resumen_no_se_confunde_con_un_id_de_avistamiento(cliente):
    # Arrange: /resumen y /<int:id> comparten prefijo; la ruta debe resolver bien
    # Act
    respuesta = cliente.get('/avistamientos/resumen')
    # Assert
    assert respuesta.status_code == 200
    assert respuesta.is_json
