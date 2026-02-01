"""
The business logic for encounters service.
"""

from datetime import datetime
import logging
import uuid
from zoneinfo import ZoneInfo

from .daos import get_encounter_dao
from ..models.encounters import PendingEncounter, Encounter, Metadata

UTC = ZoneInfo("UTC")


def utcnow() -> datetime:
    """get the current UTC time as dt-aware datetime"""
    return datetime.now(UTC)


def is_duplicate_request(idemp_key):
    """Idempotence check"""
    return False


def add_encounter(pe: PendingEncounter, now=None) -> str:
    logger = logging.getLogger("controller")
    logger.debug("Adding pending encounter")

    new_id = str(uuid.uuid4()).replace("-", "")
    dao = get_encounter_dao()

    created_at = (now or utcnow()).isoformat()
    item = Encounter(
        encounter_id=new_id,
        metadata=Metadata(
            created_at=created_at,
            updated_at=created_at,
            created_by=pe.username,
        ),
        patient_id=pe.patient_id,
        provider_id=pe.provider_id,
        encounter_date=pe.encounter_date,
        encounter_type=pe.encounter_type,
        clinical_data=pe.clinical_data,
    )

    dao.add_encounter(item)

    return new_id


def get_encounter(encounter_id: str) -> Encounter:
    """
    Throws a KeyError if the encounter doesnt exist.
    """
    dao = get_encounter_dao()
    return dao.get_encounter(encounter_id)
