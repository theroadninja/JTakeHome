import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from encounters.service import app, Settings
from encounters.controllers.controller import utcnow
from encounters.controllers.daos import get_encounter_dao

mock_settings = Settings(
    api_key="U",
    log_level="DEBUG",
)
headers = {"x-api-key": "U"}


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
