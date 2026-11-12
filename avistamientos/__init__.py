"""API de avistamientos de aves organizada con arquitectura hexagonal (Cockburn, 2005).

- hexagono/     : la aplicación (reglas de negocio, casos de uso y puertos). No conoce tecnologías.
- adaptadores/  : traducen entre una tecnología concreta y un puerto del hexágono.
    - primarios/   lado que conduce la aplicación (HTTP con Flask).
    - secundarios/ lado que la aplicación conduce (SQLite, reloj del sistema).
"""
