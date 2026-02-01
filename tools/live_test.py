#!/usr/bin/env python3
import datetime
import requests
from zoneinfo import ZoneInfo

UTC = ZoneInfo("UTC")

def utcnow():
    # datetime.utcnow() is deprecated :(
    return datetime.datetime.now(UTC)


if __name__ == "__main__":
    base_url = "http://localhost:8000"
    headers = {"x-api-key": "1"}

    resp = requests.post(
        url=f"{base_url}/encounters",
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
    print(resp)
    print(resp.text)