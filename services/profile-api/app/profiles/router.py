import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..database import get_db
from .models import Profile
from .schemas import ProfileCreate, ProfileList, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/v1/profiles", tags=["profiles"])

DB = Annotated[Session, Depends(get_db)]

NOT_FOUND = {404: {"description": "Profile not found."}}
CONFLICT = {409: {"description": "A profile with this email already exists."}}


def _get_or_404(db: Session, profile_id: uuid.UUID) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile


def _email_taken(db: Session, email: str, exclude_id: uuid.UUID | None = None) -> bool:
    query = select(Profile.id).where(Profile.email == email)
    if exclude_id is not None:
        query = query.where(Profile.id != exclude_id)
    return db.execute(query).first() is not None


def _commit_or_409(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A profile with this email already exists.")


@router.get("", response_model=ProfileList)
def list_profiles(
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    last_name: Annotated[str | None, Query(description="Exact match, case-insensitive.")] = None,
    email: Annotated[str | None, Query(description="Exact match, case-insensitive.")] = None,
) -> ProfileList:
    """List profiles, newest first, with optional filters."""
    query = select(Profile)
    if last_name is not None:
        query = query.where(func.lower(Profile.last_name) == last_name.lower())
    if email is not None:
        query = query.where(Profile.email == email.strip().lower())

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(
        query.order_by(Profile.created_at.desc(), Profile.id).limit(page_size).offset((page - 1) * page_size)
    ).all()
    return ProfileList(items=items, page=page, page_size=page_size, total=total)


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED, responses=CONFLICT)
def create_profile(body: ProfileCreate, db: DB) -> Profile:
    """Create a profile."""
    if _email_taken(db, body.email):
        raise HTTPException(status_code=409, detail="A profile with this email already exists.")
    profile = Profile(**body.model_dump())
    db.add(profile)
    _commit_or_409(db)
    return profile


@router.get("/{profile_id}", response_model=ProfileRead, responses=NOT_FOUND)
def get_profile(profile_id: uuid.UUID, db: DB) -> Profile:
    """Get one profile by ID."""
    return _get_or_404(db, profile_id)


@router.patch("/{profile_id}", response_model=ProfileRead, responses={**NOT_FOUND, **CONFLICT})
def update_profile(profile_id: uuid.UUID, body: ProfileUpdate, db: DB) -> Profile:
    """Update some fields of a profile. Fields you leave out are unchanged."""
    profile = _get_or_404(db, profile_id)
    changes = body.model_dump(exclude_unset=True)
    if "email" in changes and _email_taken(db, changes["email"], exclude_id=profile.id):
        raise HTTPException(status_code=409, detail="A profile with this email already exists.")
    for field, value in changes.items():
        setattr(profile, field, value)
    _commit_or_409(db)
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND)
def delete_profile(profile_id: uuid.UUID, db: DB) -> Response:
    """Delete a profile permanently."""
    profile = _get_or_404(db, profile_id)
    db.delete(profile)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
