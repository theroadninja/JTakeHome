import logging

from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from encounters.logging import setup_logging
from pydantic_settings import BaseSettings

# reads a http header field
header_scheme = APIKeyHeader(name="x-api-key")


class Settings(BaseSettings):
    """
    fastapi automagically maps all env vars based on field names
    """

    api_key: str
    log_level: str = "DEBUG"


# ##########
# globals forced by fastapi's design
settings = Settings()
app = FastAPI()
# ##########


@app.on_event("startup")
def startup():
    setup_logging(settings.log_level)
    logger = logging.getLogger("server")
    logger.info("STARTUP LOG 123-123-1234")


@app.get("/")
async def root(key: str = Depends(header_scheme)):
    logger = logging.getLogger("server")
    if key != settings.api_key:
        return header_scheme.make_not_authenticated_error()

    logger.info("TEST LOG 123-123-1234")
    return {"test": "hello", "k": key}
