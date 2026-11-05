"""Load sample profiles. Run with: python -m app.seed"""

from datetime import date

from sqlalchemy import select

from .database import SessionLocal
from .profiles.models import Profile

SAMPLE_PROFILES = [
    dict(first_name="Ada", last_name="Lovelace", date_of_birth=date(1990, 12, 10),
         email="ada@example.com", phone="+442071234567", city="London", country="GB"),
    dict(first_name="Grace", last_name="Hopper", date_of_birth=date(1986, 12, 9),
         email="grace@example.com", phone="+12125550147", city="New York", country="US"),
    dict(first_name="Alan", last_name="Turing", date_of_birth=date(1992, 6, 23),
         email="alan@example.com", phone=None, city="Manchester", country="GB"),
]


def main() -> None:
    added = 0
    with SessionLocal() as db:
        for data in SAMPLE_PROFILES:
            if db.scalar(select(Profile.id).where(Profile.email == data["email"])) is None:
                db.add(Profile(**data))
                added += 1
        db.commit()
    print(f"Seeded {added} profile(s).")


if __name__ == "__main__":
    main()
