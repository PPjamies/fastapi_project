import uuid
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from ..constants import (
    CITY_MAX_LENGTH,
    COUNTRY_PATTERN,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_PATTERN,
)

Name = Annotated[str, Field(min_length=1, max_length=NAME_MAX_LENGTH)]
Email = Annotated[EmailStr, Field(max_length=EMAIL_MAX_LENGTH)]
Phone = Annotated[str, Field(pattern=PHONE_PATTERN, description="E.164 format, e.g. +14155550123")]
City = Annotated[str, Field(min_length=1, max_length=CITY_MAX_LENGTH)]
Country = Annotated[str, Field(pattern=COUNTRY_PATTERN, description="ISO 3166-1 alpha-2 code, e.g. GB")]


def _not_in_future(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    return value


def _lowercase(value: str | None) -> str | None:
    return value.strip().lower() if value is not None else None


class ProfileCreate(BaseModel):
    """Body for POST /v1/profiles."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "date_of_birth": "1990-12-10",
                "email": "ada@example.com",
                "phone": "+442071234567",
                "city": "London",
                "country": "GB",
            }
        },
    )

    first_name: Name
    last_name: Name
    date_of_birth: date
    email: Email
    phone: Phone | None = None
    city: City | None = None
    country: Country | None = None

    _dob = field_validator("date_of_birth")(_not_in_future)
    _email = field_validator("email")(_lowercase)


REQUIRED_FIELDS = ("first_name", "last_name", "date_of_birth", "email")


class ProfileUpdate(BaseModel):
    """Body for PATCH /v1/profiles/{profile_id}. Send only the fields you want to change."""

    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {"city": "Paris", "country": "FR"}})

    first_name: Name | None = None
    last_name: Name | None = None
    date_of_birth: date | None = None
    email: Email | None = None
    phone: Phone | None = None
    city: City | None = None
    country: Country | None = None

    _dob = field_validator("date_of_birth")(_not_in_future)
    _email = field_validator("email")(_lowercase)

    @model_validator(mode="after")
    def required_fields_cannot_be_null(self):
        cleared = [name for name in REQUIRED_FIELDS if name in self.model_fields_set and getattr(self, name) is None]
        if cleared:
            raise ValueError(f"These fields cannot be null: {', '.join(cleared)}")
        return self


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    email: str
    phone: str | None
    city: str | None
    country: str | None
    created_at: datetime
    updated_at: datetime


class ProfileList(BaseModel):
    items: list[ProfileRead]
    page: int
    page_size: int
    total: int
