import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..constants import CITY_MAX_LENGTH, EMAIL_MAX_LENGTH, NAME_MAX_LENGTH
from ..database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    # Stored lowercase so uniqueness is case-insensitive
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(16), nullable=True)
    city: Mapped[str | None] = mapped_column(String(CITY_MAX_LENGTH), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )
