"""Casos de uso de la aplicación. Implementa el puerto de entrada GestionDeAvistamientos.

Coordina la regla de negocio (validador) y el puerto de salida RepositorioDeAvistamientos.
No sabe si quien lo llama es HTTP, un script o una prueba, ni si los datos van a SQLite o a memoria.
"""
from avistamientos.hexagono.errores import NoEncontrado
from avistamientos.hexagono.puertos import GestionDeAvistamientos, RepositorioDeAvistamientos
from avistamientos.hexagono.validacion import ValidadorDeAvistamiento


class ServicioDeAvistamientos(GestionDeAvistamientos):
    def __init__(self, repositorio: RepositorioDeAvistamientos, validador: ValidadorDeAvistamiento):
        self._repositorio = repositorio
        self._validador = validador

    def listar(self) -> list:
        return self._repositorio.listar()

    def resumen(self) -> list:
        return self._repositorio.resumen()

    def consultar(self, identificador: int) -> dict:
        avistamiento = self._repositorio.obtener(identificador)
        if avistamiento is None:
            raise NoEncontrado(identificador)
        return avistamiento

    def crear(self, datos) -> dict:
        limpios = self._validador.validar(datos)
        return self._repositorio.crear(limpios)

    def actualizar(self, identificador: int, datos) -> dict:
        # Se verifica la existencia antes de validar: un id inexistente es 404, no 400.
        self.consultar(identificador)
        limpios = self._validador.validar(datos)
        return self._repositorio.actualizar(identificador, limpios)

    def eliminar(self, identificador: int) -> None:
        if not self._repositorio.eliminar(identificador):
            raise NoEncontrado(identificador)
