from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Service


def list_services(db: Session, category: str | None = None):
    query = select(Service).options(joinedload(Service.category))
    if category is not None:
        query = query.join(Service.category).where(Category.slug == category)
    return db.scalars(query.order_by(Service.name, Service.id)).all()


def get_service(db: Session, service_id: int):
    return db.scalar(
        select(Service)
        .options(joinedload(Service.category))
        .where(Service.id == service_id)
    )
