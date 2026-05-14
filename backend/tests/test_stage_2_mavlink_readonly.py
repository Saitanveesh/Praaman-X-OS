import inspect
from pathlib import Path

from app.core.enums import TelemetrySource
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.plugins.mavlink_readonly_provider import MAVLinkReadOnlyProvider
from app.services.telemetry_service import TelemetryService
from app.services.telemetry_source_service import TelemetrySourceService


def test_telemetry_source_switching_keeps_mock_default_and_mavlink_read_only():
    init_db()
    service = TelemetrySourceService()
    with SessionLocal() as db:
        active = service.get_active_source(db) or service.set_active_source(db, TelemetrySource.MOCK)
        assert active.source_type == TelemetrySource.MOCK.value
        selected = service.set_active_source(db, TelemetrySource.MAVLINK_READ_ONLY)
        assert selected.source_type == TelemetrySource.MAVLINK_READ_ONLY.value
        assert selected.read_only is True
        assert selected.status == "ACTIVE"
        restored = service.set_active_source(db, TelemetrySource.MOCK)
        assert restored.source_type == TelemetrySource.MOCK.value


def test_mavlink_provider_fails_gracefully_without_required_dependency_or_stream():
    provider = MAVLinkReadOnlyProvider()
    status = provider.connect(host="127.0.0.1", port=14699, protocol="UDP")
    assert status["connected"] is False
    assert status["read_only"] is True
    assert status["commands_enabled"] is False
    assert "no mavlink stream received" in (status["last_error"] or "").lower()
    assert provider.poll_once() is None


def test_mavlink_provider_is_read_only_and_has_no_command_sending_methods():
    provider = MAVLinkReadOnlyProvider()
    public_methods = {name for name, value in inspect.getmembers(provider, predicate=callable) if not name.startswith("_")}
    assert {"connect", "disconnect", "is_connected", "get_status", "poll_once", "poll_loop"}.issubset(public_methods)
    forbidden = {"command" + "_long_send", "set" + "_mode_send", "mission" + "_item_send", "mission" + "_count_send", "mission" + "_write_partial_list_send", "param" + "_set_send", "send", "write"}
    assert public_methods.isdisjoint(forbidden)


def test_telemetry_history_endpoint_data_model_works_for_mavlink_payloads():
    init_db()
    payload = {
        "drone_id": "PX-QD-001",
        "lat": 12.9716,
        "lon": 77.5946,
        "altitude_m": 40.0,
        "speed_mps": 4.0,
        "heading_deg": 180.0,
        "battery_percent": 88,
        "mode": "MAVLINK_READ_ONLY",
        "armed": False,
        "gps_status": "GOOD",
        "link_state": "FULL_LINK",
        "mission_state": "IDLE",
        "warnings": ["MAVLINK_READ_ONLY_TELEMETRY"],
    }
    with SessionLocal() as db:
        service = TelemetryService()
        saved = service.save(db, payload)
        history = service.history(db, "PX-QD-001", limit=10)
    assert saved.mode == "MAVLINK_READ_ONLY"
    assert any(row.mode == "MAVLINK_READ_ONLY" for row in history)


def test_mavlink_status_shape_and_source_contains_no_unsafe_send_patterns():
    provider = MAVLinkReadOnlyProvider()
    status = provider.get_status()
    assert status["read_only"] is True
    assert status["commands_enabled"] is False
    assert "message_counts" in status
    source = Path("app/plugins/mavlink_readonly_provider.py").read_text()
    unsafe_patterns = ["command" + "_long_send", "set" + "_mode_send", "mission" + "_item_send", "mission" + "_count_send", "mission" + "_write_partial_list_send", "param" + "_set_send", "mav" + ".send"]
    for unsafe in unsafe_patterns:
        assert unsafe not in source
