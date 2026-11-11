import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Profile
from .schemas import ProfileIn, ProfileOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # create the table on startup if it doesn't exist
    yield


app = FastAPI(title="Profile API", lifespan=lifespan)


def get_profile_or_404(db: Session, profile_id: uuid.UUID) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profile not found")
    return profile


def commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use")


@app.post("/profiles", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(body: ProfileIn, db: Session = Depends(get_db)):
    profile = Profile(**body.model_dump())
    db.add(profile)
    commit(db)
    return profile


@app.get("/profiles", response_model=list[ProfileOut])
def list_profiles(db: Session = Depends(get_db)):
    return db.scalars(select(Profile)).all()


@app.get("/profiles/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_profile_or_404(db, profile_id)


@app.put("/profiles/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: uuid.UUID, body: ProfileIn, db: Session = Depends(get_db)):
    profile = get_profile_or_404(db, profile_id)
    for field, value in body.model_dump().items():
        setattr(profile, field, value)
    commit(db)
    return profile


@app.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(profile_id: uuid.UUID, db: Session = Depends(get_db)):
    db.delete(get_profile_or_404(db, profile_id))
    db.commit()
