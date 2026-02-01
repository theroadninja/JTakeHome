"""
Data Access Objects for Encounter Service
"""

import logging

from encounters.models import Encounter


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
        self.audit_logs = []

    def add_log(self):
        pass

    def list_logs(self):
        pass


# global var to simulate a database
enc_dao = EncounterDao()


def get_encounter_dao():
    return enc_dao
