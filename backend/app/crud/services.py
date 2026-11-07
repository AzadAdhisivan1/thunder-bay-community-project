from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Service


def services_query(category: str | None = None) -> Select:
    """All services, or one category's, by name. Shared by the list and distance queries."""
    query = select(Service).options(joinedload(Service.category))
    if category is not None:
        query = query.join(Service.category).where(Category.slug == category)
    return query.order_by(Service.name, Service.id)


def service_query(service_id: int) -> Select:
    return select(Service).options(joinedload(Service.category)).where(Service.id == service_id)


def list_services(db: Session, category: str | None = None):
    return db.scalars(services_query(category)).all()


def get_service(db: Session, service_id: int):
    return db.scalar(service_query(service_id))
