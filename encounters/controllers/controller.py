"""
The business logic for encounters service.
"""

from datetime import datetime
import logging
import time
import uuid
from typing import List
from zoneinfo import ZoneInfo

from .daos import get_encounter_dao, get_audit_dao
from ..models import AccessLogEntry, TYPE_ENCOUNTER, CREATE, READ
from ..models.encounters import PendingEncounter, Encounter, Metadata

UTC = ZoneInfo("UTC")


def utcnow() -> datetime:
    """get the current UTC time as dt-aware datetime"""
    return datetime.now(UTC)


def is_duplicate_request(idemp_key):
    """Idempotence check"""
    return False


def username_from_key(api_key):
    # pretend there is a mapping from api_key to username
    return "dcupp"


def _now():
    return int(time.time() * 1000)


def _read_entry(timestamp, username, eid) -> AccessLogEntry:
    return AccessLogEntry(
        timestamp_epoch_ms=timestamp,
        username=username,
        item_type=TYPE_ENCOUNTER,
        item_id=eid,
        access_type=READ,
    )


def add_encounter(username: str, pe: PendingEncounter, now=None) -> str:
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
            created_by=username,
        ),
        patient_id=pe.patient_id,
        provider_id=pe.provider_id,
        encounter_date=pe.encounter_date,
        encounter_type=pe.encounter_type,
        clinical_data=pe.clinical_data,
    )

    dao.add_encounter(item)
    get_audit_dao().add_entry(
        AccessLogEntry(
            timestamp_epoch_ms=int(time.time() * 1000),
            username=username,
            item_type=TYPE_ENCOUNTER,
            item_id=new_id,
            access_type=CREATE,
        )
    )

    return new_id


def get_encounter(username: str, encounter_id: str) -> Encounter:
    """
    Throws a KeyError if the encounter doesnt exist.
    """
    dao = get_encounter_dao()
    enc = dao.get_encounter(encounter_id)

    get_audit_dao().add_entry(_read_entry(_now(), username, encounter_id))
    return enc


def list_encounters(
    username: str,
    start_date: str = None,
    end_date: str = None,
    patient_id: str = None,
    provider_id: str = None,
):
    dao = get_encounter_dao()
    audit = get_audit_dao()
    results = dao.search_encounters(start_date, end_date, patient_id, provider_id)
    ts = _now()
    for enc in results:
        audit.add_entry(_read_entry(ts, username, enc.encounter_id))
    return results


def list_audit_entries(start_ms: int, end_ms: int) -> List[AccessLogEntry]:
    dao = get_audit_dao()
    return dao.list_entries(start_ms, end_ms)
