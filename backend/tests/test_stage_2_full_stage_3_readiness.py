from pathlib import Path

from fastapi.testclient import TestClient

from app.core.enums import TelemetrySource
from app.db.init_db import init_db
from app.main import app
from app.services.mavlink_readonly_runtime import mavlink_readonly_provider

client = TestClient(app)


def test_mavlink_diagnostics_endpoint_shape():
    response = client.get("/api/mavlink-readonly/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert data["read_only"] is True
    assert data["command_sending_enabled"] is False
    assert data["protocol"] == "UDP"
    assert {"HEARTBEAT", "GLOBAL_POSITION_INT", "VFR_HUD", "SYS_STATUS", "GPS_RAW_INT", "ATTITUDE", "BATTERY_STATUS"}.issubset(data["message_counts"].keys())


def test_mavlink_safety_endpoint_disables_hardware_control():
    response = client.get("/api/mavlink-readonly/safety")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "read_only": True,
        "command_sending_enabled": False,
        "mission_upload_enabled": False,
        "parameter_write_enabled": False,
        "mode_change_enabled": False,
        "arming_enabled": False,
        "takeoff_enabled": False,
        "hardware_control_enabled": False,
    }


def test_mavlink_unavailable_source_switch_fails_safely():
    init_db()
    mavlink_readonly_provider.disconnect()
    response = client.post("/api/telemetry-sources/active", json={"source_type": TelemetrySource.MAVLINK_READ_ONLY.value})
    assert response.status_code == 200
    data = response.json()
    assert data["active_source"] == TelemetrySource.MOCK.value
    assert data["status"] == "ERROR"
    assert data["read_only"] is True
    assert "Staying on MOCK" in data["message"]


def test_mock_source_switch_response_is_stable():
    response = client.post("/api/telemetry-sources/active", json={"source_type": TelemetrySource.MOCK.value})
    assert response.status_code == 200
    data = response.json()
    assert data["active_source"] == TelemetrySource.MOCK.value
    assert data["status"] == "ACTIVE"
    assert data["read_only"] is True


def test_bench_readiness_endpoint():
    response = client.get("/api/bench/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["stage"] == "STAGE_3_PIXHAWK_BENCH_READINESS"
    assert data["bench_mode"] is True
    assert data["read_only"] is True
    assert data["hardware_commands_enabled"] is False
    assert len(data["checklist"]) >= 9


def test_connection_profiles_list_endpoint_has_seed_profiles():
    response = client.get("/api/connection-profiles")
    assert response.status_code == 200
    profile_ids = {item["profile_id"] for item in response.json()}
    assert {"sitl-udp-14550", "mavproxy-udp-14550", "pixhawk-serial-placeholder", "playback-placeholder"}.issubset(profile_ids)


def test_no_mavlink_provider_unsafe_command_patterns():
    source = Path("app/plugins/mavlink_readonly_provider.py").read_text()
    unsafe_patterns = [
        "command" + "_long_send",
        "set" + "_mode_send",
        "mission" + "_item_send",
        "mission" + "_count_send",
        "mission" + "_write_partial_list_send",
        "param" + "_set_send",
        "mav" + ".send",
    ]
    for pattern in unsafe_patterns:
        assert pattern not in source
