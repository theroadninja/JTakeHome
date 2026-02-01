"""
Data Access Objects for Encounter Service
"""

import logging

from encounters.models import Encounter, AccessLogEntry


class EncounterDao:
    def __init__(self):
        # map id -> encounter
        self.encounters = dict()

    def add_encounter(self, enc: Encounter):
        logger = logging.getLogger("daos")
        if enc.encounter_id in self.encounters:
            raise KeyError(f"encounter {enc.encounter_id} already exists")
        self.encounters[enc.encounter_id] = enc
        logger.debug(f"There are now {len(self.encounters)} encounters")

    def get_encounter(self, encounter_id):
        return self.encounters[encounter_id]

    def get_count(self):
        return len(self.encounters)


class AuditDao:
    def __init__(self):
        self.audit_entries = []

    def add_entry(self, entry: AccessLogEntry):
        if entry.timestamp_epoch_ms < 0:
            # this shouldnt happen
            raise ValueError(f"invalid timestamp: {entry.timestamp_epoch_ms}")
        self.audit_entries.append(entry)
        self.audit_entries = sorted(
            self.audit_entries,
            key=lambda e: e.timestamp_epoch_ms,
        )

    def list_entries(self, start_ms, end_ms):
        """
        start_ms and end_ms are both inclusive
        """
        results = []
        for entry in self.audit_entries:
            if start_ms and start_ms > entry.timestamp_epoch_ms:
                continue
            if end_ms and end_ms < entry.timestamp_epoch_ms:
                return results
            results.append(entry)

        return results



    def get_count(self):
        return len(self.audit_entries)


# global var to simulate a database
enc_dao = EncounterDao()
audit_dao = AuditDao()


def _reset_daos():
    """quick hack for testing"""
    global enc_dao
    global audit_dao
    enc_dao = EncounterDao()
    audit_dao = AuditDao()


def get_encounter_dao():
    return enc_dao


def get_audit_dao():
    return audit_dao
