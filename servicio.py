"""Casos de uso: coordina validador y repositorio. No conoce HTTP."""


class NoEncontrado(Exception):
    """No existe un avistamiento con ese id."""


class ServicioDeAvistamientos:
    def __init__(self, repositorio, validador):
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
