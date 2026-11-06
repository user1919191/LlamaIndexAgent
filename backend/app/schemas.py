import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.security import validate_password, validate_username


def validate_email(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value) or len(value) > 254:
        raise ValueError("invalid email")
    return value


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = None
    school: str | None = Field(default=None, max_length=128)
    major: str | None = Field(default=None, max_length=128)

    @field_validator("username")
    @classmethod
    def username_value(cls, value: str) -> str:
        return validate_username(value)

    @field_validator("password")
    @classmethod
    def password_value(cls, value: str) -> str:
        return validate_password(value)

    @field_validator("email")
    @classmethod
    def email_value(cls, value: str | None) -> str | None:
        return validate_email(value)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def username_value(cls, value: str) -> str:
        return validate_username(value)


class ProfileUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = None
    school: str | None = Field(default=None, max_length=128)
    major: str | None = Field(default=None, max_length=128)

    model_config = ConfigDict(extra="forbid")

    @field_validator("email")
    @classmethod
    def email_value(cls, value: str | None) -> str | None:
        return validate_email(value)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_new_password(self):
        self.new_password = validate_password(self.new_password)
        if self.old_password == self.new_password:
            raise ValueError("new password must differ from old password")
        return self
