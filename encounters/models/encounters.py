from typing import Any

from pydantic import BaseModel


class Metadata(BaseModel):
    created_at: str  # TODO validate iso date?
    updated_at: str
    created_by: str  # a.k.a. username (the spec required created_by)


class PendingEncounter(BaseModel):
    idempotence_key: str
    # no encounter id yet
    username: str
    patient_id: str
    provider_id: str
    encounter_date: str  # "timestamp"
    encounter_type: str  # TODO choice list:  initial_assessment, follow_up, treatment_session
    clinical_data: Any


class Encounter(BaseModel):
    encounter_id: str  # supposed to be auto generated
    metadata: Metadata
    patient_id: str
    provider_id: str
    encounter_date: str  # "timestamp"
    encounter_type: str  # TODO choice list:  initial_assessment, follow_up, treatment_session
    clinical_data: Any


# TODO move to another file
class AccessLogEntry(BaseModel):
    timestamp_epoch_ms: int
    user_id: str  # who access it
    item_type: str  # encounter
    item_id: str  # encounter id
    access_type: str  # create, read, update
