"""
This is the entry point (sort of) for the server.
The true entrypoint lies within fastapi's code.  But this is the "main" file.
I am trying to contain all of fastapi's strangeness here.
"""

import logging
from http.client import HTTPException

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings

from encounters.logging import setup_logging
from encounters.models.encounters import PendingEncounter, expect_iso_date
from encounters.controllers import controller

# reads a http header field
header_scheme = APIKeyHeader(name="x-api-key")


class Settings(BaseSettings):
    """
    fastapi automagically maps all env vars based on field names
    """

    api_key: str
    log_level: str = "DEBUG"


# ####################################
# globals forced by fastapi's design
_settings = None
app = FastAPI()


def settings() -> Settings:
    return _settings


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Overrides the pydantic validation so we can scrub sensitive data.
    """
    msg = "Validation errors:"
    for error in exc.errors():
        msg += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(msg, status_code=400)


@app.on_event("startup")
def startup():
    global _settings
    _settings = Settings()
    setup_logging(settings().log_level)
    logger = logging.getLogger("server")
    logger.info("server starting up in @startup()")


@app.get("/status")
async def get_status(
    key: str = Depends(header_scheme),
):
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    return {"status": "ok"}


@app.post("/encounters")
async def add_encounter(
    encounter: PendingEncounter,
    key: str = Depends(header_scheme),
):
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    if controller.is_duplicate_request(encounter.idempotence_key):
        raise Exception("idempotence not implemented yet")

    username = controller.username_from_key(key)
    new_id = controller.add_encounter(username, encounter)
    return {"encounter_id": new_id}


@app.get("/encounters")
async def list_encounters(
    start_date: str = None,
    end_date: str = None,
    patient_id: str = None,
    provider_id: str = None,
    key: str = Depends(header_scheme),
):
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    try:
        if start_date:
            expect_iso_date(start_date)
        if end_date:
            expect_iso_date(end_date)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    username = controller.username_from_key(key)
    return controller.list_encounters(username, start_date, end_date, patient_id, provider_id)


@app.get("/encounters/{encounter_id}")
async def get_encounter(
    encounter_id: str,
    key: str = Depends(header_scheme),
):
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    try:
        username = controller.username_from_key(key)
        return controller.get_encounter(username, encounter_id)
    except KeyError:
        raise HTTPException(
            status_code=400,  # BAD REQUEST
            detail="That encounter does not exist",
        )


@app.get("/audit/encounters")
async def list_audit_entries(
    start_ms: int = -1,  # this is query_param
    end_ms: int = None,  # this is a query_param
    key: str = Depends(header_scheme),
):
    """
    start_ms and end_ms are both query parameters
    """
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    # fastapi auto converts this to json
    return controller.list_audit_entries(start_ms, end_ms)
