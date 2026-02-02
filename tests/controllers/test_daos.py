import unittest
from encounters.models import AccessLogEntry, Encounter
from encounters.controllers.daos import AuditDao, EncounterDao
from encounters.utils import make_test_metadata


def make_test_entry(timestamp: int) -> AccessLogEntry:
    return AccessLogEntry(
        timestamp_epoch_ms=timestamp,
        username="dcupp",
        item_type="item",
        item_id="123",
        access_type="create",
    )

class DaoTests(unittest.TestCase):
    def test_list_audit(self):
        dao = AuditDao()

        dao.add_entry(make_test_entry(100))
        dao.add_entry(make_test_entry(200))
        dao.add_entry(make_test_entry(300))
        dao.add_entry(make_test_entry(400))

        self.assertEqual(4, len(dao.list_entries(None, None)))

        self.assertEqual(4, len(dao.list_entries(99, None)))
        self.assertEqual(4, len(dao.list_entries(100, None)))
        self.assertEqual(3, len(dao.list_entries(101, None)))

        self.assertEqual(4, len(dao.list_entries(None, 401)))
        self.assertEqual(4, len(dao.list_entries(None, 400)))
        self.assertEqual(3, len(dao.list_entries(None, 399)))

        self.assertEqual(1, len(dao.list_entries(201, 399)))

    def test_list_encounters(self):
        dao = EncounterDao()
        dao.add_encounter(
            Encounter(
                encounter_id="e1",
                metadata=make_test_metadata(),
                patient_id="p1",
                provider_id="pr5",
                encounter_date="2026-01-01",
                encounter_type="initial_assessment",
                clinical_data={},
            )
        )
        dao.add_encounter(
            Encounter(
                encounter_id="e2",
                metadata=make_test_metadata(),
                patient_id="p2",
                provider_id="pr5",
                encounter_date="2026-01-02",
                encounter_type="initial_assessment",
                clinical_data={},
            )
        )
        dao.add_encounter(
            Encounter(
                encounter_id="e3",
                metadata=make_test_metadata(),
                patient_id="p3",
                provider_id="pr6",
                encounter_date="2026-01-03",
                encounter_type="initial_assessment",
                clinical_data={},
            )
        )

        self.assertEqual(3, len(dao.search_encounters()))
        self.assertEqual(0, len(dao.search_encounters(patient_id="p0")))
        self.assertEqual(1, len(dao.search_encounters(patient_id="p1")))
        self.assertEqual(2, len(dao.search_encounters(start_date="2026-01-02")))
        self.assertEqual(1, len(dao.search_encounters(end_date="2026-01-01")))
        self.assertEqual(
            1,
            len(
                dao.search_encounters(start_date="2026-01-02", end_date="2026-01-02", patient_id="p2", provider_id="pr5")
            ),
        )
        self.assertEqual(2, len(dao.search_encounters(provider_id="pr5")))
