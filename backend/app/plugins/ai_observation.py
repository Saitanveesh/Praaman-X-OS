class AIObservationPlugin:
    def process_frame(self, frame) -> dict:
        return {"processed": False, "reason": "AI observation plugin placeholder only"}

    def get_events(self) -> list[dict]:
        return []
