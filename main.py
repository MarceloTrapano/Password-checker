from fastapi import FastAPI
import os

from src import PasswordModel, PasswordResponseModel, password_check, prepare_user_inputs


LANGUAGE_PATH = 'lang-english.txt'
with open(os.path.abspath(LANGUAGE_PATH), "r") as f:
    GLOBAL_WORDS = f.read().splitlines()

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello there! This is password checker! Please send your password check via our API!"}


@app.post("/check_password/", response_model=PasswordResponseModel)
def post_password(package: PasswordModel):
    user_inputs = prepare_user_inputs(
        username=package.username, email=package.email)

    user_inputs.extend(GLOBAL_WORDS)
    response = password_check(
        password=package.password, user_inputs=user_inputs, prev_password=package.prev_password)
    return response
