from pydantic import BaseModel, EmailStr, Field


MAX_PASSWORD_LENGTH: int = 72


class PasswordModel(BaseModel):
    """Data transfer object for password strength evaluation requests."""
    username: str
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=MAX_PASSWORD_LENGTH)
    prev_password: str | None = Field(
        default=None, max_length=MAX_PASSWORD_LENGTH)

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
