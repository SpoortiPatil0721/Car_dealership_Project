from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Purchase, User

NEWEST_FIRST = (Purchase.purchased_at.desc(), Purchase.id.desc())


class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    def for_user(self, user: User) -> list[Purchase]:
        query = select(Purchase).where(Purchase.user_id == user.id).order_by(*NEWEST_FIRST)
        return list(self.db.scalars(query))

    def all_sales(self) -> list[Purchase]:
        query = select(Purchase).options(joinedload(Purchase.buyer)).order_by(*NEWEST_FIRST)
        return list(self.db.scalars(query))
