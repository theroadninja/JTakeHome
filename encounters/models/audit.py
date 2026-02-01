from typing import Any

from pydantic import BaseModel


class AccessLogEntry(BaseModel):
    timestamp_epoch_ms: int
    user_id: str  # who access it
    item_type: str  # encounter
    item_id: str  # encounter id
    access_type: str  # create, read, update
