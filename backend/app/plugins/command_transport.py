from abc import ABC, abstractmethod


class CommandTransport(ABC):
    @abstractmethod
    async def send_command(self, command) -> dict: ...

    @abstractmethod
    async def await_ack(self, command_id: str) -> dict: ...

    @abstractmethod
    def get_transport_status(self) -> dict: ...


class MockCommandTransport(CommandTransport):
    async def send_command(self, command) -> dict:
        return {"sent": True, "transport": "mock", "command_id": command.command_id}

    async def await_ack(self, command_id: str) -> dict:
        return {"acknowledged": True, "message": f"Mock acknowledgement for {command_id}"}

    def get_transport_status(self) -> dict:
        return {"transport": "mock", "hardware_connected": False}
