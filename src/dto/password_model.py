from pydantic import BaseModel, EmailStr


class PasswordModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    prev_password: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "okenobi",
                    "email": "o.kenobi@jedi-council.com",
                    "password": "Hello there!",
                    "prev_password": "May the force be with you!"
                }
            ]
        }
    }
