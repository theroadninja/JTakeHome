import json
import unittest
from pydantic import ValidationError

from encounters.models.encounters import Metadata, Encounter
from encounters.controllers.controller import utcnow
from encounters.utils import make_test_metadata


class EncounterModelsTests(unittest.TestCase):

    def test_metadata(self):
        raw = """
        {
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00",
            "created_by": "dcupp"
        }
        """
        _ = Metadata(**json.loads(raw))

        raw2 = """
        {
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00",
            "created": "dcupp"
        }
        """
        with self.assertRaises(ValidationError):
            _ = Metadata(**json.loads(raw2))


    def test_iso_date_validation(self):
        with self.assertRaises(ValueError):
            _ = Encounter(
                encounter_id="123",
                metadata=make_test_metadata(),
                patient_id="p123",
                provider_id="pr123",
                encounter_date="12/22/1980",
                encounter_type="initial_assessment",
                clinical_data=None,
            )

        with self.assertRaises(ValueError):
            _ = Encounter(
                encounter_id="123",
                metadata=make_test_metadata(),
                patient_id="p123",
                provider_id="pr123",
                encounter_date="1980-12-22T12:00:00",
                encounter_type="initial_assessment",
                clinical_data=None,
            )

        _ = Encounter(
            encounter_id="123",
            metadata=make_test_metadata(),
            patient_id="p123",
            provider_id="pr123",
            encounter_date="1980-12-22",
            encounter_type="initial_assessment",
            clinical_data=None,
        )
