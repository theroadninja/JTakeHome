import re
from typing import Any, Literal, Annotated

from pydantic import BaseModel, AfterValidator

def expect_iso_date(s):
    """
    Throw a ValueError if s is not an ISO8601 string.
    """
    if not re.match(r"^\d\d\d\d-\d\d-\d\d$", s):
        raise ValueError(f"not a valid ISO8601 date")
    return s

def expect_iso_datetime(s):
    """
    Throw a ValueError if s is not an ISO8601 string.
    """
    if not re.match(r"^\d\d\d\d-\d\d-\d\d[ T].*", s):
        raise ValueError(f"not a valid ISO8601 date")
    return s

class Metadata(BaseModel):
    created_at: Annotated[str, AfterValidator(expect_iso_datetime)]
    updated_at: Annotated[str, AfterValidator(expect_iso_datetime)]
    created_by: str  # a.k.a. username (the spec required created_by)


class PendingEncounter(BaseModel):
    idempotence_key: str
    patient_id: str
    provider_id: str
    encounter_date: Annotated[str, AfterValidator(expect_iso_date)]
    encounter_type: Literal["initial_assessment", "follow_up", "treatment_session"]
    clinical_data: Any


class Encounter(BaseModel):
    encounter_id: str
    metadata: Metadata
    patient_id: str
    provider_id: str
    encounter_date: Annotated[str, AfterValidator(expect_iso_date)]
    encounter_type: Literal["initial_assessment", "follow_up", "treatment_session"]
    clinical_data: Any
