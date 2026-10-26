from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import search
from app.db import get_db
from app.schemas import ServiceOut

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[ServiceOut])
def search_services(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query must not be blank")
    return search.search_services(db, query)
