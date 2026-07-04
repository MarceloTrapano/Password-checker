from fastapi import FastAPI
from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import os

from src import PasswordModel, PasswordResponseModel, password_check, prepare_user_inputs, password_logger


LANGUAGE_PATH: str = 'lang-english.txt'
COMMON_PASSWORDS_PATH: str = 'common_passwords.txt'
with open(os.path.abspath(LANGUAGE_PATH), "r") as f:
    GLOBAL_WORDS: set[str] = set(f.read().splitlines())

with open(os.path.abspath(COMMON_PASSWORDS_PATH), "r") as f:
    COMMON_PASSWORDS: set[str] = set(f.read().splitlines())

SENSITIVE_FIELDS: set[str] = {"password", "prev_password"}

app: FastAPI = FastAPI()

logger = password_logger(__name__)


@app.get("/")
def home() -> dict[str, str]:
    """Root API response.

    Returns:
        dict[str, str]: welcoming message.
    """
    logger.info("Recieved get request!")
    return {"message": "Hello there! This is password checker! Please send your password check via our API!"}


@app.post("/check_password/", response_model=PasswordResponseModel)
def post_password(package: PasswordModel) -> dict[str, str | int | bool | list[str]]:
    """Validate user password.

    Args:
        package (PasswordModel): password package with credentials such as username, email and optional previous password.

    Returns:
        dict[str, str | int | bool | list[str]]: password strength evaluation.
    """
    logger.info("Recieved password to check.")
    user_inputs: list[str] = prepare_user_inputs(
        username=package.username, email=package.email)

    user_inputs.extend(GLOBAL_WORDS)
    response: dict[str, str | int | bool | list[str]] = password_check(
        password=package.password,
        user_inputs=user_inputs,
        prev_password=package.prev_password,
        common_passwords=COMMON_PASSWORDS)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles Pydantic validation errors by logging the details and returning a 422 response.

    Args:
        request (Request): the incoming HTTP request object.
        exc (RequestValidationError): the exception containing the validation errors.

    Returns:
        JSONResponse: a response with status 422 containing the validation details.
    """
    sanitized_errors: list[dict] = []
    for error in exc.errors():
        error = dict(error)
        if error.get("loc") and error["loc"][-1] in SENSITIVE_FIELDS:
            error["input"] = "***REDACTED***"
        sanitized_errors.append(error)

    logger.error(
        f"Validation error: {sanitized_errors} | Request path: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": sanitized_errors},
    )
