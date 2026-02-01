import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from encounters.service import app, Settings
from encounters.controllers.controller import utcnow
from encounters.controllers.daos import get_encounter_dao, _reset_daos, get_audit_dao
from encounters.models import Encounter, Metadata, AccessLogEntry

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
    def test_unauthorized(self, settings_fn):
        settings_fn.return_value = mock_settings

        resp = self.client.get("/status")
        self.assertEqual(401, resp.status_code)

        resp = self.client.get(
            "/status",
            headers=headers,
        )
        self.assertEqual(200, resp.status_code)

    @patch("encounters.service.settings")
    def test_add_encounter(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()
        c1 = get_encounter_dao().get_count()
        resp = self.client.post(
            "/encounters",
            headers=headers,
            json={
                "idempotence_key": "abc",
                "patient_id": "p123",
                "provider_id": "pr456",
                "encounter_date": "2026-01-01",
                "encounter_type": "initial_assessment",
                "clinical_data": {},
            },
        )
        self.assertEqual(200, resp.status_code)
        self.assertEqual(c1 + 1, get_encounter_dao().get_count())
        self.assertEqual(1, get_audit_dao().get_count())

    @patch("encounters.service.settings")
    def test_bad_literals(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()
        resp = self.client.post(
            "/encounters",
            headers=headers,
            json={
                "idempotence_key": "abc",
                "patient_id": "p123",
                "provider_id": "pr456",
                "encounter_date": utcnow().isoformat(),
                "encounter_type": "south_park",
                "clinical_data": {},
            },
        )
        self.assertEqual(400, resp.status_code)
        self.assertTrue("encounter_type" in resp.text)

    @patch("encounters.service.settings")
    def test_get_encounter(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()

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
        self.assertEqual(1, get_audit_dao().get_count())

    @patch("encounters.service.settings")
    def test_get_encounter_doesnt_exist(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()

        eid = "0a8245"
        resp = self.client.get(
            f"/encounters/{eid}",
            headers=headers,
        )
        self.assertEqual(400, resp.status_code)
        self.assertTrue("does not exist" in resp.text)
        self.assertEqual(0, get_audit_dao().get_count())

    @patch("encounters.service.settings")
    def test_list_audit_empty(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()

        resp = self.client.get(
            f"/audit/encounters",
            headers=headers,
        )
        self.assertEqual(200, resp.status_code)
        mylist = resp.json()
        self.assertEqual(0, len(mylist))

    @patch("encounters.service.settings")
    def test_audit_log(self, settings_fn):
        settings_fn.return_value = mock_settings
        _reset_daos()
        resp = self.client.post(
            "/encounters",
            headers=headers,
            json={
                "idempotence_key": "abc",
                "patient_id": "p123",
                "provider_id": "pr456",
                "encounter_date": "2026-01-01",
                "encounter_type": "initial_assessment",
                "clinical_data": {},
            },
        )
        self.assertEqual(200, resp.status_code)
        encounter1 = resp.json()["encounter_id"]

        resp = self.client.get(
            f"/encounters/{encounter1}",
            headers=headers,
        )
        self.assertEqual(200, resp.status_code)
        resp = self.client.get(
            f"/encounters/{encounter1}",
            headers=headers,
        )
        self.assertEqual(200, resp.status_code)

        # no time params
        url = f"/audit/encounters"
        resp = self.client.get(url, headers=headers)
        self.assertEqual(200, resp.status_code)
        mylist = resp.json()
        self.assertEqual(3, len(mylist))

        mylist = [AccessLogEntry(**i) for i in mylist]

        for i in range(3):
            self.assertEqual(encounter1, mylist[i].item_id)
        self.assertEqual("create", mylist[0].access_type)
        self.assertEqual("read", mylist[1].access_type)
        self.assertEqual("read", mylist[1].access_type)

        end_ms = int(time.time() * 1000) + 2000
        url = f"/audit/encounters?start_ms=0&end_ms={end_ms}"
        resp = self.client.get(url, headers=headers)
        self.assertEqual(200, resp.status_code)
        mylist = resp.json()
        self.assertEqual(3, len(mylist))
