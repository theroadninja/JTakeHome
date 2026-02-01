from typing import Any

from pydantic import BaseModel


class Metadata(BaseModel):
    created_at: str
    updated_at: str
    created_by: str  # a.k.a. username (the spec required created_by)


class PendingEncounter(BaseModel):
    idempotence_key: str
    username: str
    patient_id: str
    provider_id: str
    encounter_date: str
    encounter_type: str  # initial_assessment, follow_up, treatment_session
    clinical_data: Any


class Encounter(BaseModel):
    encounter_id: str
    metadata: Metadata
    patient_id: str
    provider_id: str
    encounter_date: str
    encounter_type: str  # initial_assessment, follow_up, treatment_session
    clinical_data: Any
