import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import services
from app.core.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter()

EMAIL_TAKEN = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="This email address is already registered",
)


def get_existing_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> User:
    db_user = services.get_user_by_uuid(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if services.get_user_by_email(db, email=user.email):
        raise EMAIL_TAKEN
    try:
        return services.create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise EMAIL_TAKEN


@router.get("/{user_id}", response_model=UserResponse)
def retrieve_user(db_user: User = Depends(get_existing_user)):
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user: UserUpdate, db_user: User = Depends(get_existing_user), db: Session = Depends(get_db)):
    if user.email and user.email != db_user.email:
        if services.get_user_by_email(db, email=user.email):
            raise EMAIL_TAKEN
    try:
        return services.update_user(db, db_user=db_user, user=user)
    except IntegrityError:
        db.rollback()
        raise EMAIL_TAKEN


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db_user: User = Depends(get_existing_user), db: Session = Depends(get_db)):
    services.delete_user(db, db_user=db_user)

@router.get("", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()
