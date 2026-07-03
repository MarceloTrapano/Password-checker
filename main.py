from fastapi import FastAPI

from src import PasswordModel

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello there! This is password checker! Please send your password check via our API!"}


@app.post("/check_password")
def read_root(package: PasswordModel):
    return package.password
