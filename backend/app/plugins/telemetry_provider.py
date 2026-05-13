from abc import ABC, abstractmethod


class TelemetryProvider(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def read_telemetry(self) -> dict: ...

    @abstractmethod
    def is_connected(self) -> bool: ...
