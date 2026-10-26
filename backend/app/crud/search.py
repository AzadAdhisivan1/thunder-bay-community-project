from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Category, Service


def search_services(db: Session, text: str):
    # Treat LIKE metacharacters as literal user input, not wildcard operators.
    escaped = text.replace("/", "//").replace("%", "/%").replace("_", "/_")
    pattern = f"%{escaped}%"
    return db.scalars(
        select(Service)
        .join(Service.category)
        .options(joinedload(Service.category))
        .where(or_(
            Service.name.ilike(pattern, escape="/"),
            Category.name.ilike(pattern, escape="/"),
            Service.description.ilike(pattern, escape="/"),
        ))
        .order_by(Service.name, Service.id)
    ).all()
