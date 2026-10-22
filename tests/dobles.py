"""Dobles de prueba compartidos por las pruebas unitarias e de integración."""


class RelojFijo:
    """STUB: devuelve siempre la misma fecha. Hace determinista la regla "no posterior a hoy"."""

    def __init__(self, fecha):
        self._fecha = fecha

    def hoy(self):
        return self._fecha


class RepositorioEnMemoria:
    """FAKE: implementación funcional (dict) con la misma interfaz que RepositorioSQLite."""

    def __init__(self):
        self._datos = {}
        self._siguiente = 1

    def listar(self):
        return [dict(v) for _, v in sorted(self._datos.items())]

    def resumen(self):
        cuentas = {}
        for v in self._datos.values():
            cuentas[v['especie']] = cuentas.get(v['especie'], 0) + 1
        return [{'especie': e, 'cantidad': c} for e, c in sorted(cuentas.items())]

    def obtener(self, identificador):
        v = self._datos.get(identificador)
        return dict(v) if v else None

    def crear(self, datos):
        registro = {'id': self._siguiente, **datos}
        self._datos[self._siguiente] = registro
        self._siguiente += 1
        return dict(registro)

    def actualizar(self, identificador, datos):
        if identificador not in self._datos:
            return None
        self._datos[identificador] = {'id': identificador, **datos}
        return dict(self._datos[identificador])

    def eliminar(self, identificador):
        return self._datos.pop(identificador, None) is not None
