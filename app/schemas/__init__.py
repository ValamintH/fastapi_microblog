from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "Gandalf",
                    "username": "Gandalf",
                    "email": "gandalf@mail.com",
                    "password_hash": "ba7816bf8...",
                }
            ]
        },
        "from_attributes": True,
    }


class UserInSchema(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "Gandalf",
                "email": "gandalf@mail.com",
                "password": "gandalf3047BC",
            }
        }


class TokenSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
            }
        }
