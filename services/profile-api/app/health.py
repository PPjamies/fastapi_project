from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db

router = APIRouter(tags=["health"])


class Health(BaseModel):
    status: str
    database: str


@router.get("/health", response_model=Health)
def health(db: Annotated[Session, Depends(get_db)]) -> Health:
    """Check that the API and its database are reachable."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable.")
    return Health(status="ok", database="ok")
