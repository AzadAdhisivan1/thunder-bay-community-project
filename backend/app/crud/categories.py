from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category


def list_categories(db: Session):
    return db.scalars(
        select(Category).where(Category.services.any()).order_by(Category.name, Category.id)
    ).all()
