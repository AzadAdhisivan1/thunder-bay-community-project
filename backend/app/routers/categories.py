from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import categories
from app.db import get_db
from app.schemas import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return categories.list_categories(db)
