from pydantic import BaseModel, EmailStr


class PasswordModel(BaseModel):
    username: str
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "okenobi",
                    "email": "o.kenobi@jedi-council.com",
                    "password": "Hello there!"
                }
            ]
        }
    }
