"""Puertos del hexágono: las conversaciones con propósito que la aplicación tiene con el exterior.

Los puertos son interfaces (clases abstractas) declaradas DENTRO del hexágono. Los adaptadores,
que viven afuera, las implementan (puertos de salida) o las usan (puerto de entrada). Así todas
las dependencias de código apuntan hacia el hexágono, nunca al revés.
"""
from abc import ABC, abstractmethod
from datetime import date


# ---------------------------------------------------------------- puerto de entrada (primario)

class GestionDeAvistamientos(ABC):
    """Lo que la aplicación ofrece a quien la conduce (HTTP, un script, una prueba)."""

    @abstractmethod
    def listar(self) -> list:
        """Todos los avistamientos ordenados por id."""

    @abstractmethod
    def resumen(self) -> list:
        """Cantidad de avistamientos por especie, ordenado por especie."""

    @abstractmethod
    def consultar(self, identificador: int) -> dict:
        """El avistamiento con ese id. Lanza NoEncontrado si no existe."""

    @abstractmethod
    def crear(self, datos) -> dict:
        """Valida, guarda y devuelve el avistamiento creado. Lanza ErrorDeValidacion."""

    @abstractmethod
    def actualizar(self, identificador: int, datos) -> dict:
        """Reemplaza un avistamiento. Lanza NoEncontrado (primero) o ErrorDeValidacion."""

    @abstractmethod
    def eliminar(self, identificador: int) -> None:
        """Elimina un avistamiento. Lanza NoEncontrado si no existe."""


# ---------------------------------------------------------------- puertos de salida (secundarios)

class RepositorioDeAvistamientos(ABC):
    """Lo que la aplicación necesita para guardar y recuperar avistamientos."""

    @abstractmethod
    def listar(self) -> list:
        """Lista de diccionarios ordenada por id."""

    @abstractmethod
    def resumen(self) -> list:
        """Lista de {'especie', 'cantidad'} ordenada por especie."""

    @abstractmethod
    def obtener(self, identificador: int):
        """El diccionario del avistamiento, o None si no existe."""

    @abstractmethod
    def crear(self, datos: dict) -> dict:
        """Guarda los datos y devuelve el registro con su id asignado."""

    @abstractmethod
    def actualizar(self, identificador: int, datos: dict):
        """Reemplaza el registro y lo devuelve, o None si no existe."""

    @abstractmethod
    def eliminar(self, identificador: int) -> bool:
        """True si existía y se eliminó, False si no existía."""


class Reloj(ABC):
    """Lo que la aplicación necesita para saber qué día es "hoy"."""

    @abstractmethod
    def hoy(self) -> date:
        """La fecha de hoy."""
