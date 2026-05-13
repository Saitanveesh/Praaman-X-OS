class MapProvider:
    def get_map_status(self) -> dict:
        return {"provider": "placeholder", "offline_ready": False}

    def get_vehicle_position(self) -> dict | None:
        return None

    def get_route(self) -> list[dict]:
        return []
