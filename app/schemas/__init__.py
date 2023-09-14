from pydantic import BaseModel


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
