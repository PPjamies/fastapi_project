import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# fields shared across reading and writing
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None


# mandatory field needed to create a user
class UserCreate(UserBase):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 bytes")
        return v


# optional fields that can be updated
class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

    @field_validator("first_name", "last_name", "email")
    @classmethod
    def not_null(cls, v):
        if v is None:
            raise ValueError("may be omitted but cannot be null")
        return v


# what the api sends back over the network
class UserResponse(UserBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)  # don't panic and convert from map to dot notation


class UserPage(BaseModel):
    items: list[UserResponse]
    next_cursor: uuid.UUID | None
