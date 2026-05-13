from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SystemEvent:
    event_type: str
    payload: dict[str, Any]
    timestamp: datetime = datetime.now(timezone.utc)
