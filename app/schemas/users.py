import datetime
import re

from pydantic import BaseModel, EmailStr, model_validator, Field

from app.enums import UserRole
from app.exceptions import RegisterError
from app.schemas.base import ORMBase


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=40)
    confirm_password: str = Field(min_length=8, max_length=40)

    @model_validator(mode='after')
    def validate_password(self):
        if self.password != self.confirm_password:
            raise RegisterError('Пароли не совпадают')

        if not re.search(r"^(?=.*\d)(?=.*[A-Z]).+$", self.password):
            raise RegisterError("Пароль должен содержать хотя бы одну цифру и одну заглавную букву")

        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UserResponse(ORMBase):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime.datetime


class PasswordChange(BaseModel):
    password: str = Field(min_length=8, max_length=40)
    confirm_password: str = Field(min_length=8, max_length=40)

    @model_validator(mode='after')
    def validate_password(self):
        if self.password != self.confirm_password:
            raise RegisterError('Пароли не совпадают')

        if not re.search(r"^(?=.*\d)(?=.*[A-Z]).+$", self.password):
            raise RegisterError("Пароль должен содержать хотя бы одну цифру и одну заглавную букву")

        return self


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
