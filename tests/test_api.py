import pytest
from app import crear_app


@pytest.fixture
def cliente(tmp_path):
    app = crear_app({'TESTING': True, 'DATABASE': str(tmp_path / 'pruebas.db')})
    return app.test_client()


def test_flujo_crud(cliente):
    assert cliente.get('/avistamientos').json == []
    datos = {'especie': 'colibrí', 'lugar': 'Bogotá', 'fecha': '2026-09-29', 'observador': 'Ana'}
    respuesta = cliente.post('/avistamientos', json=datos)
    assert respuesta.status_code == 201
    identificador = respuesta.json['id']
    assert cliente.get(f'/avistamientos/{identificador}').status_code == 200
    assert len(cliente.get('/avistamientos').json) == 1
    assert cliente.get('/avistamientos/resumen').json == [{'especie': 'colibrí', 'cantidad': 1}]
    nuevos = {**datos, 'especie': 'garza'}
    assert cliente.put(f'/avistamientos/{identificador}', json=nuevos).json['especie'] == 'garza'
    assert cliente.delete(f'/avistamientos/{identificador}').status_code == 204
    assert cliente.get(f'/avistamientos/{identificador}').status_code == 404
    assert cliente.delete(f'/avistamientos/{identificador}').status_code == 404


def test_validaciones(cliente):
    assert cliente.post('/avistamientos', json={'especie': 'búho'}).status_code == 400
    assert cliente.post('/avistamientos', json={'especie': 'búho', 'lugar': 'Bosque', 'fecha': '2026-02-30', 'observador': 'Luis'}).status_code == 400
    assert cliente.put('/avistamientos/999', json={}).status_code == 404
