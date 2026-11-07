from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Service


def search_query(text: str) -> Select:
    """Services whose name, category or description contain `text`, by name."""
    # Treat LIKE metacharacters as literal user input, not wildcard operators.
    escaped = text.replace("/", "//").replace("%", "/%").replace("_", "/_")
    pattern = f"%{escaped}%"
    return (
        select(Service)
        .join(Service.category)
        .options(joinedload(Service.category))
        .where(or_(
            Service.name.ilike(pattern, escape="/"),
            Category.name.ilike(pattern, escape="/"),
            Service.description.ilike(pattern, escape="/"),
        ))
        .order_by(Service.name, Service.id)
    )


def search_services(db: Session, text: str):
    return db.scalars(search_query(text)).all()
