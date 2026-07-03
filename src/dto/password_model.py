from pydantic import BaseModel, EmailStr


class PasswordModel(BaseModel):
    """Data transfer object for password strength evaluation requests."""
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
