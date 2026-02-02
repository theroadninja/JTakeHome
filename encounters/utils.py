from encounters.controllers.controller import utcnow
from encounters.models import Metadata


def make_test_metadata():
    now = utcnow().isoformat()
    return Metadata(
        created_at=now,
        updated_at=now,
        created_by=now,
    )
