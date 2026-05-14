from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

MAVLINK_MESSAGE_TYPES = [
    "HEARTBEAT",
    "GLOBAL_POSITION_INT",
    "VFR_HUD",
    "SYS_STATUS",
    "GPS_RAW_INT",
    "ATTITUDE",
    "BATTERY_STATUS",
]


class MAVLinkReadOnlyProvider:
    """Receive-only MAVLink telemetry provider.

    Stage 2.0 safety boundary: this adapter opens receive-oriented connections,
    parses telemetry messages, and intentionally exposes no command transmit API.
    It must not call MAVLink send/write methods or mutate vehicle state.
    """

    def __init__(self) -> None:
        self.host = "127.0.0.1"
        self.port = 14550
        self.protocol = "UDP"
        self._connection: Any | None = None
        self._last_error: str | None = None
        self._last_values: dict[str, Any] = {}
        self._message_counts: dict[str, int] = {message_type: 0 for message_type in MAVLINK_MESSAGE_TYPES}
        self._last_message_time: datetime | None = None
        self._endpoint = "udpin:127.0.0.1:14550"
        self._connected_at: datetime | None = None
        self._received_since_connect = False

    def connect(self, host: str = "127.0.0.1", port: int = 14550, protocol: str = "UDP") -> dict[str, Any]:
        self.disconnect()
        self.host = host or "127.0.0.1"
        self.port = int(port or 14550)
        self.protocol = (protocol or "UDP").upper()
        self._last_error = None
        self._last_values = {}
        self._message_counts = {message_type: 0 for message_type in MAVLINK_MESSAGE_TYPES}
        self._last_message_time = None
        self._received_since_connect = False

        if self.protocol == "TCP":
            self._last_error = "TCP MAVLink read-only is structured as an experimental placeholder and disabled in Stage 2.0."
            return self.get_status()
        if self.protocol == "SERIAL":
            self._last_error = "Serial MAVLink read-only is a future Pixhawk bench placeholder and disabled in Stage 2.0."
            return self.get_status()
        if self.protocol != "UDP":
            self._last_error = f"Unsupported MAVLink read-only protocol: {self.protocol}"
            return self.get_status()

        try:
            from pymavlink import mavutil  # type: ignore
        except ImportError:
            self._last_error = "pymavlink is not installed; MAVLink read-only telemetry is unavailable."
            return self.get_status()

        self._endpoint = f"udpin:{self.host}:{self.port}"
        try:
            # udpin binds a local UDP socket and waits for a SITL/MAVProxy/MAVLink Router
            # stream. No heartbeat or command messages are transmitted by this provider.
            self._connection = mavutil.mavlink_connection(
                self._endpoint,
                autoreconnect=True,
                source_system=255,
                source_component=0,
                input=True,
            )
            self._connected_at = datetime.now(timezone.utc)
            first_message = self._connection.recv_match(type=MAVLINK_MESSAGE_TYPES, blocking=True, timeout=1.0)
            if first_message is None:
                self._last_error = f"No MAVLink stream received on {self._endpoint}"
                self.disconnect()
                self._last_error = f"No MAVLink stream received on {self._endpoint}"
                return self.get_status()
            message_type = first_message.get_type()
            self._message_counts[message_type] = self._message_counts.get(message_type, 0) + 1
            self._last_message_time = datetime.now(timezone.utc)
            self._received_since_connect = True
            self._merge_message(first_message)
            return self.get_status()
        except Exception as exc:  # provider boundary must fail safely
            self._connection = None
            self._last_error = f"No MAVLink stream received on {self._endpoint}: {exc}"
            return self.get_status()

    def disconnect(self) -> dict[str, Any]:
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception as exc:
                self._last_error = f"MAVLink read-only disconnect warning: {exc}"
        self._connection = None
        return self.get_status()

    def is_connected(self) -> bool:
        return self._connection is not None

    def get_status(self) -> dict[str, Any]:
        return {
            "connected": self.is_connected(),
            "read_only": True,
            "commands_enabled": False,
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "endpoint": self._endpoint,
            "last_error": self._last_error,
            "last_message_time": self._last_message_time.isoformat() if self._last_message_time else None,
            "message_counts": dict(self._message_counts),
            "received_since_connect": self._received_since_connect,
            "supported_protocols": {"UDP": "FUNCTIONAL", "TCP": "EXPERIMENTAL_DISABLED", "SERIAL": "PLACEHOLDER_DISABLED"},
        }

    def poll_once(self) -> Optional[dict[str, Any]]:
        if self._connection is None:
            self._last_error = self._last_error or "MAVLink read-only provider is not connected."
            return None
        try:
            message = self._connection.recv_match(type=MAVLINK_MESSAGE_TYPES, blocking=False)
        except Exception as exc:
            self._last_error = f"MAVLink read-only telemetry read failed: {exc}"
            return None
        if message is None:
            return None

        message_type = message.get_type()
        self._message_counts[message_type] = self._message_counts.get(message_type, 0) + 1
        self._last_message_time = datetime.now(timezone.utc)
        self._received_since_connect = True
        self._last_error = None
        self._merge_message(message)
        return self._to_telemetry_payload()

    def poll_loop(self) -> None:
        # FastAPI owns scheduling in app.main.telemetry_loop; this method exists for the
        # plugin interface and intentionally performs only one receive pass per call.
        self.poll_once()

    def _merge_message(self, message: Any) -> None:
        message_type = message.get_type()
        if message_type == "GLOBAL_POSITION_INT":
            self._last_values["lat"] = message.lat / 1e7
            self._last_values["lon"] = message.lon / 1e7
            if getattr(message, "relative_alt", None) is not None:
                self._last_values["altitude_m"] = message.relative_alt / 1000
                self._last_values["relative_alt_available"] = True
            hdg = getattr(message, "hdg", 65535)
            if hdg != 65535:
                self._last_values["heading_deg"] = hdg / 100
        elif message_type == "VFR_HUD":
            self._last_values["speed_mps"] = float(getattr(message, "groundspeed", self._last_values.get("speed_mps", 0.0)))
            if not self._last_values.get("relative_alt_available"):
                self._last_values["altitude_m"] = float(getattr(message, "alt", self._last_values.get("altitude_m", 0.0)))
            self._last_values["heading_deg"] = float(getattr(message, "heading", self._last_values.get("heading_deg", 0.0)))
        elif message_type == "SYS_STATUS":
            remaining = getattr(message, "battery_remaining", -1)
            if remaining is not None and remaining >= 0:
                self._last_values["battery_percent"] = max(0, min(100, int(remaining)))
        elif message_type == "BATTERY_STATUS":
            remaining = getattr(message, "battery_remaining", -1)
            if remaining is not None and remaining >= 0:
                self._last_values["battery_percent"] = max(0, min(100, int(remaining)))
        elif message_type == "GPS_RAW_INT":
            fix_type = int(getattr(message, "fix_type", 0) or 0)
            if fix_type >= 3:
                self._last_values["gps_status"] = "GOOD"
            elif fix_type == 2:
                self._last_values["gps_status"] = "DEGRADED"
            else:
                self._last_values["gps_status"] = "BAD"
        elif message_type == "HEARTBEAT":
            base_mode = int(getattr(message, "base_mode", 0) or 0)
            self._last_values["armed"] = bool(base_mode & 128)
            self._last_values["base_mode"] = base_mode
            self._last_values["system_status"] = getattr(message, "system_status", None)
            self._last_values["vehicle_type"] = getattr(message, "type", None)
            self._last_values["mode"] = self._decode_mode(message)
        elif message_type == "ATTITUDE":
            self._last_values["attitude_seen"] = True

    def _decode_mode(self, message: Any) -> str:
        if self._connection is not None:
            try:
                return str(self._connection.flightmode)
            except Exception:
                pass
        custom_mode = getattr(message, "custom_mode", None)
        return f"MAVLINK_MODE_{custom_mode}" if custom_mode is not None else "MAVLINK_READ_ONLY"

    def _to_telemetry_payload(self) -> dict[str, Any]:
        required = ["lat", "lon", "altitude_m", "speed_mps", "heading_deg", "battery_percent", "gps_status", "mode"]
        warnings = ["MAVLINK_READ_ONLY_TELEMETRY"]
        if any(key not in self._last_values for key in required):
            warnings.append("MAVLINK_PARTIAL_TELEMETRY")
        return {
            "drone_id": "PX-QD-001",
            "lat": float(self._last_values.get("lat", 0.0)),
            "lon": float(self._last_values.get("lon", 0.0)),
            "altitude_m": float(self._last_values.get("altitude_m", 0.0)),
            "speed_mps": float(self._last_values.get("speed_mps", 0.0)),
            "heading_deg": float(self._last_values.get("heading_deg", 0.0)),
            "battery_percent": int(self._last_values.get("battery_percent", 0)),
            "mode": str(self._last_values.get("mode", "MAVLINK_READ_ONLY")),
            "armed": bool(self._last_values.get("armed", False)),
            "gps_status": str(self._last_values.get("gps_status", "UNKNOWN")),
            "link_state": "FULL_LINK",
            "mission_state": "IDLE",
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc),
        }
