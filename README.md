# JTakeHome

This implements a "partient encounter API".

To set up:

```
pyenv virtualenv 3.11.5 enc
pyenv shell enc
pip3 install -r requirements-dev.txt
```


To run:

```
API_KEY=1 fastapi dev encounters/service
```

To verify it is working:

```
curl -X GET  http://localhost:8000/status --header "x-api-key: 1" -H "Content-Type: application/json"
```

## Authentication

Authentication is done using a static, per-user secret token passed with the http
header `x-api-key` on every request.

## Requirements

- PII Redaction:  done with  "log formatter" in `encounters/logging/__init__.py`
- Error messages dont leak sensitive info:  implemented by custom `validation_exception_handler()` in `encounters/service/__init__.py`
- Schema validation:  this is done by using pydantic (classes extending `BaseModel` in `encounters/models/encounters.py`).   Fastapi automatically tries to coerce inputs into these classes, and unexpected data causes failures.  I intercept the messages so that no sensitive data is leaked.
- Validate all inputs at API boundaries:   most inputs are "automatically" validated behind the scenes by fastapi using = 
pydantic, so the rules are expressed as field annotations on the pydantic models.  I implemented one custom annotation in order to force ISO8601 formats.  See `encounters/models/encounters.py`

## Design and Testability

The main areas of this application are:
1. the REST API - `encounters/service`,
2. the data classes - `encounters/models`
2. the business logic - `encounters/controllers`
3. the data layer - `encounters/controllers/daos.py`

Due to fastapi's design, the data models are deliberately couples to the API.  This lets you change the API by just
changing a python class.

The business logic and data layer can be tested completely independently of the REST API service methods.

The service methods can be tested independently of the real storage layer.

## Changes for Production

1. use a real database
2. API keys would come from a database instead of from ENV (right now this is a one-user system)
3. validating query params would use fastapi features for consistency
4. all errors would be wrapped in a standard structure that contains an error code and a human-readable string
5. implement idempotence
6. we might want to have two layers of data classes, so that the storage layer is not coupled to the API.
But this means we lost some of the advertised benefits of fastapi.
7. containerize