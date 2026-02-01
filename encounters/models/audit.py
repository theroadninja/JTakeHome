from typing import Any

from pydantic import BaseModel

TYPE_ENCOUNTER = "encounter"

CREATE = "create"
READ = "read"


class AccessLogEntry(BaseModel):
    timestamp_epoch_ms: int
    username: str  # who access it
    item_type: str  # encounter
    item_id: str  # encounter id
    access_type: str  # create, read
