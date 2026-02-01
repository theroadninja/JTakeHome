import json
import unittest
from pydantic import ValidationError

from encounters.models.encounters import Metadata


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
