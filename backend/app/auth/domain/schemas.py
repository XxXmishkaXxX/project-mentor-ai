from pydantic import BaseModel, EmailStr, Field

from app.users.domain.schemas import UserResponse


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user: UserResponse
