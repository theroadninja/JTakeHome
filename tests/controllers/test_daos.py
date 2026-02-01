import unittest
from encounters.models import AccessLogEntry
from encounters.controllers.daos import AuditDao


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
