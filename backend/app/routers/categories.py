from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """US-02: return only categories that have at least one service.

    Owner: Santhosh. Replace the line below with a call into app/crud/.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet (US-02)")
