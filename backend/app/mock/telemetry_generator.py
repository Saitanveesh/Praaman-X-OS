import math
from datetime import datetime, timezone


class MockTelemetryGenerator:
    def __init__(self):
        self.tick = 0
        self.base_lat = 12.9716
        self.base_lon = 77.5946

    def next(self) -> dict:
        self.tick += 1
        phase = self.tick / 10
        battery = max(20, 82 - self.tick // 30)
        warnings = []
        if battery < 30:
            warnings.append("LOW_BATTERY_SIMULATION")
        return {
            "drone_id": "PX-QD-001",
            "lat": round(self.base_lat + math.sin(phase) * 0.0008, 7),
            "lon": round(self.base_lon + math.cos(phase) * 0.0008, 7),
            "altitude_m": round(35.2 + math.sin(phase) * 2, 1),
            "speed_mps": round(6.5 + math.cos(phase) * 0.8, 1),
            "heading_deg": round((92 + self.tick * 3) % 360, 1),
            "battery_percent": battery,
            "mode": "GUIDED",
            "armed": False,
            "gps_status": "GOOD",
            "link_state": "FULL_LINK",
            "mission_state": "IDLE",
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc),
        }
