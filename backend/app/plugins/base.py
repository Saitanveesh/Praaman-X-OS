from abc import ABC, abstractmethod


class Plugin(ABC):
    name: str

    @abstractmethod
    def status(self) -> dict:
        """Return plugin status suitable for API diagnostics."""
