"""
This is the entry point (sort of) for the server.
The true entrypoint lies within fastapi's code.  But this is the "main" file.
I am trying to contain all of fastapi's strangeness here.
"""

import logging
from http.client import HTTPException

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings

from encounters.logging import setup_logging
from encounters.models.encounters import PendingEncounter
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


# ####################################


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
    logger.info("STARTUP LOG 123-123-1234")


@app.get("/")
async def root(key: str = Depends(header_scheme)):
    logger = logging.getLogger("server")
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    logger.info("TEST LOG 123-123-1234")
    return {"test": "hello", "k": key}


@app.post("/encounters")
async def add_encounter(
    encounter: PendingEncounter,
    key: str = Depends(header_scheme),
):
    if key != settings().api_key:
        return header_scheme.make_not_authenticated_error()

    if controller.is_duplicate_request(encounter.idempotence_key):
        raise Exception("idempotence not implemented yet")

    new_id = controller.add_encounter(encounter)
    return {"encounter_id": new_id}
