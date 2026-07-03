from fastapi import FastAPI
import os

from src import PasswordModel, PasswordResponseModel, password_check, prepare_user_inputs


LANGUAGE_PATH: str = 'lang-english.txt'
with open(os.path.abspath(LANGUAGE_PATH), "r") as f:
    GLOBAL_WORDS: list[str] = f.read().splitlines()

app: FastAPI = FastAPI()


@app.get("/")
def home() -> dict[str, str]:
    """Root API response.

    Returns:
        dict[str, str]: welcoming message.
    """
    return {"message": "Hello there! This is password checker! Please send your password check via our API!"}


@app.post("/check_password/", response_model=PasswordResponseModel)
def post_password(package: PasswordModel) -> dict[str, str | int | bool | list[str]]:
    """Validate user password.

    Args:
        package (PasswordModel): password package with credentials such as username, email and optional previous password.

    Returns:
        dict[str, str | int | bool | list[str]]: password strength evaluation.
    """
    user_inputs: list[str] = prepare_user_inputs(
        username=package.username, email=package.email)

    user_inputs.extend(GLOBAL_WORDS)
    response: dict[str, str | int | bool | list[str]] = password_check(
        password=package.password, user_inputs=user_inputs, prev_password=package.prev_password)
    return response
