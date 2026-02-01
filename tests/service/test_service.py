import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from encounters.service import app, Settings
from encounters.controllers.controller import utcnow
from encounters.controllers.daos import get_encounter_dao
from encounters.models import Encounter, Metadata

mock_settings = Settings(
    api_key="U",
    log_level="DEBUG",
)
headers = {"x-api-key": "U"}


def make_test_metadata():
    now = utcnow().isoformat()
    return Metadata(
        created_at=now,
        updated_at=now,
        created_by=now,
    )


def make_test_encounter(eid=None):
    eid = eid or "9a71363882264730860abab050564e45"
    return Encounter(
        encounter_id=eid,
        metadata=make_test_metadata(),
        patient_id="p123",
        provider_id="pr456",
        encounter_date="2026-01-01",
        encounter_type="initial_assessment",
        clinical_data={},
    )


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("encounters.service.settings")
    def test_root(self, settings_fn):
        settings_fn.return_value = mock_settings
        _ = self.client.get("/", headers=headers)

    @patch("encounters.service.settings")
    def test_add_encounter(self, settings_fn):
        settings_fn.return_value = mock_settings
        c1 = get_encounter_dao().get_count()
        _ = self.client.post(
            "/encounters",
            headers=headers,
            json={
                "idempotence_key": "abc",
                "username": "dcupp",
                "patient_id": "p123",
                "provider_id": "pr456",
                "encounter_date": utcnow().isoformat(),
                "encounter_type": "inital_assessment",
                "clinical_data": {},
            },
        )
        self.assertEqual(c1 + 1, get_encounter_dao().get_count())

    @patch("encounters.service.settings")
    def test_get_encounter(self, settings_fn):
        settings_fn.return_value = mock_settings

        eid = "9a7136"
        enc = make_test_encounter(eid)
        dao = get_encounter_dao()
        dao.add_encounter(enc)

        resp = self.client.get(
            f"/encounters/{eid}",
            headers=headers,
        )
        enc2 = Encounter(**resp.json())
        self.assertEqual(enc, enc2)

    @patch("encounters.service.settings")
    def test_get_encounter_doesnt_exist(self, settings_fn):
        settings_fn.return_value = mock_settings

        eid = "0a8245"
        resp = self.client.get(
            f"/encounters/{eid}",
            headers=headers,
        )
        self.assertEqual(400, resp.status_code)
        self.assertTrue("does not exist" in resp.text)
