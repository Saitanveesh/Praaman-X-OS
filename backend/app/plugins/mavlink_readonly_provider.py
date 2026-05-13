from datetime import datetime, timezone
from typing import Any


class MAVLinkReadOnlyProvider:
    """Read-only MAVLink telemetry adapter for future SITL use.

    This class intentionally exposes no command-sending method and never writes MAVLink
    messages. It only attempts to consume telemetry from a UDP endpoint.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 14550, protocol: str = "UDP") -> None:
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self._connection: Any | None = None
        self._last_error: str | None = None
        self._last_values: dict[str, Any] = {}

    def connect(self) -> bool:
        try:
            from pymavlink import mavutil  # type: ignore
        except ImportError:
            self._last_error = "pymavlink is not installed; MAVLink read-only telemetry is unavailable."
            self._connection = None
            return False

        try:
            if self.protocol != "UDP":
                self._last_error = f"Unsupported read-only MAVLink protocol: {self.protocol}"
                return False
            self._connection = mavutil.mavlink_connection(f"udp:{self.host}:{self.port}", autoreconnect=True)
            self._last_error = None
            return True
        except Exception as exc:  # provider boundary must fail gracefully
            self._last_error = f"MAVLink read-only connection failed: {exc}"
            self._connection = None
            return False

    def disconnect(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception as exc:
                self._last_error = f"MAVLink read-only disconnect warning: {exc}"
        self._connection = None

    def is_connected(self) -> bool:
        return self._connection is not None

    def read_telemetry(self) -> dict[str, Any] | None:
        if self._connection is None:
            self._last_error = self._last_error or "MAVLink read-only provider is not connected."
            return None
        try:
            message = self._connection.recv_match(
                type=["HEARTBEAT", "GLOBAL_POSITION_INT", "VFR_HUD", "SYS_STATUS", "GPS_RAW_INT", "ATTITUDE"],
                blocking=False,
            )
            if message is None:
                return None
            self._merge_message(message)
            if "lat" not in self._last_values or "lon" not in self._last_values:
                return None
            return {
                "drone_id": "PX-QD-001",
                "lat": self._last_values.get("lat", 0.0),
                "lon": self._last_values.get("lon", 0.0),
                "altitude_m": self._last_values.get("altitude_m", 0.0),
                "speed_mps": self._last_values.get("speed_mps", 0.0),
                "heading_deg": self._last_values.get("heading_deg", 0.0),
                "battery_percent": self._last_values.get("battery_percent", 0),
                "mode": self._last_values.get("mode", "UNKNOWN"),
                "armed": self._last_values.get("armed", False),
                "gps_status": self._last_values.get("gps_status", "UNKNOWN"),
                "link_state": "FULL_LINK",
                "mission_state": "IDLE",
                "warnings": ["MAVLINK_READ_ONLY_TELEMETRY"],
                "timestamp": datetime.now(timezone.utc),
            }
        except Exception as exc:
            self._last_error = f"MAVLink read-only telemetry read failed: {exc}"
            return None

    def get_status(self) -> dict[str, Any]:
        return {
            "connected": self.is_connected(),
            "read_only": True,
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "last_error": self._last_error,
            "commands_enabled": False,
        }

    def _merge_message(self, message: Any) -> None:
        message_type = message.get_type()
        if message_type == "GLOBAL_POSITION_INT":
            self._last_values["lat"] = message.lat / 1e7
            self._last_values["lon"] = message.lon / 1e7
            self._last_values["altitude_m"] = message.relative_alt / 1000
            self._last_values["heading_deg"] = (message.hdg / 100) if getattr(message, "hdg", 65535) != 65535 else self._last_values.get("heading_deg", 0.0)
        elif message_type == "VFR_HUD":
            self._last_values["speed_mps"] = float(getattr(message, "groundspeed", 0.0))
            self._last_values["heading_deg"] = float(getattr(message, "heading", self._last_values.get("heading_deg", 0.0)))
            self._last_values["altitude_m"] = float(getattr(message, "alt", self._last_values.get("altitude_m", 0.0)))
        elif message_type == "SYS_STATUS":
            remaining = getattr(message, "battery_remaining", -1)
            self._last_values["battery_percent"] = max(0, int(remaining)) if remaining is not None and remaining >= 0 else 0
        elif message_type == "GPS_RAW_INT":
            fix_type = getattr(message, "fix_type", 0)
            self._last_values["gps_status"] = "GOOD" if fix_type >= 3 else "DEGRADED"
        elif message_type == "HEARTBEAT":
            base_mode = getattr(message, "base_mode", 0)
            self._last_values["armed"] = bool(base_mode & 128)
            self._last_values["mode"] = "MAVLINK_READ_ONLY"
