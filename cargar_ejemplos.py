"""Carga avistamientos ficticios sin eliminar datos existentes.

Es un segundo adaptador primario (un script por lotes): conduce la aplicación por el mismo
puerto de entrada que usa HTTP, así los ejemplos pasan por la misma regla de negocio.
Ya no escribe SQL propio.

Ejecutar: python cargar_ejemplos.py
"""
from app import app, construir_servicio

EJEMPLOS = [
    ('Cóndor de los Andes', 'Parque Nacional Natural Los Nevados, Tolima', '2026-08-02', 'Mariana Torres'),
    ('Barranquero andino', 'Jardín Botánico de Bogotá', '2026-08-04', 'Andrés Rojas'),
    ('Tángara multicolor', 'Reserva Natural Río Ñambí, Nariño', '2026-08-07', 'Camila Rodríguez'),
    ('Garza blanca', 'Humedal La Conejera, Bogotá', '2026-08-11', 'Felipe Moreno'),
    ('Colibrí', 'Jardín Botánico de Bogotá', '2026-08-15', 'Laura Pérez'),
    ('Tucán pechiblanco', 'Leticia, Amazonas', '2026-08-19', 'Daniel Cárdenas'),
    ('Guacamaya roja', 'Puerto Nariño, Amazonas', '2026-08-22', 'Natalia Gómez'),
    ('Búho currucutú', 'Villa de Leyva, Boyacá', '2026-08-27', 'Juan Sebastián Díaz'),
    ('Martín pescador', 'Lago de Tota, Boyacá', '2026-09-01', 'Valentina Ruiz'),
    ('Flamenco americano', 'Santuario de Fauna y Flora Los Flamencos, La Guajira', '2026-09-03', 'Sofía Herrera'),
    ('Pelícano pardo', 'Santa Marta, Magdalena', '2026-09-06', 'Mateo Gutiérrez'),
    ('Águila pescadora', 'Embalse del Guavio, Cundinamarca', '2026-09-10', 'Paula Jiménez'),
    ('Colibrí', 'Monserrate, Bogotá', '2026-09-14', 'Sergio'),
    ('Garza blanca', 'Humedal Juan Amarillo, Bogotá', '2026-09-18', 'Juliana Castro'),
    ('Carpintero real', 'Parque Arví, Medellín', '2026-09-21', 'Emilio Salazar'),
    ('Pava caucana', 'Reserva Otún Quimbaya, Risaralda', '2026-09-26', 'Isabella Restrepo'),
    ('Turpial', 'Valledupar, Cesar', '2026-10-02', 'David Martínez'),
    ('Colibrí', 'Parque Nacional Natural Chingaza, Cundinamarca', '2026-10-08', 'Alejandra Muñoz'),
]

CAMPOS = ('especie', 'lugar', 'fecha', 'observador')


def cargar():
    ruta = app.config['DATABASE']
    gestion = construir_servicio(ruta)
    # Evitar insertar dos veces exactamente el mismo ejemplo.
    existentes = {tuple(a[c] for c in CAMPOS) for a in gestion.listar()}
    creados = 0
    for ejemplo in EJEMPLOS:
        if ejemplo not in existentes:
            gestion.crear(dict(zip(CAMPOS, ejemplo)))
            existentes.add(ejemplo)
            creados += 1
    print(f'Se agregaron {creados} avistamientos de ejemplo en {ruta}.')
    print('No se eliminaron los registros anteriores. Los ejemplos son ficticios.')


if __name__ == '__main__':
    cargar()
