from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import services
from app.db import get_db
from app.schemas import ServiceOut

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
def list_services(category: str | None = None, db: Session = Depends(get_db)):
    return services.list_services(db, category)


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = services.get_service(db, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
