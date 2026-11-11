import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class ProfileIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None


class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
