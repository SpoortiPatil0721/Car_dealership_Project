from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Purchase, Vehicle
from app.schemas import CategoryCount, StatsSummary, TopSeller


class StatsService:
    def __init__(self, db: Session, low_stock_threshold: int):
        self.db = db
        self.low_stock_threshold = low_stock_threshold

    def summary(self) -> StatsSummary:
        models, units, value, sold_out = self.db.execute(
            select(
                func.count(Vehicle.id),
                func.coalesce(func.sum(Vehicle.quantity), 0),
                func.coalesce(func.sum(Vehicle.price * Vehicle.quantity), 0),
                func.count(Vehicle.id).filter(Vehicle.quantity == 0),
            )
        ).one()
        units_sold, revenue = self.db.execute(
            select(
                func.coalesce(func.sum(Purchase.quantity), 0),
                func.coalesce(func.sum(Purchase.unit_price * Purchase.quantity), 0),
            )
        ).one()
        return StatsSummary(
            total_models=models,
            units_in_stock=units,
            inventory_value=round(value, 2),
            out_of_stock=sold_out,
            units_sold=units_sold,
            revenue=round(revenue, 2),
            low_stock=self._low_stock(),
            top_sellers=self._top_sellers(),
            by_category=self._by_category(),
        )

    def _low_stock(self) -> list[Vehicle]:
        query = (
            select(Vehicle)
            .where(Vehicle.quantity <= self.low_stock_threshold)
            .order_by(Vehicle.quantity, Vehicle.make, Vehicle.model)
        )
        return list(self.db.scalars(query))

    def _top_sellers(self, limit: int = 5) -> list[TopSeller]:
        units = func.sum(Purchase.quantity)
        query = (
            select(Purchase.make, Purchase.model, units, func.sum(Purchase.unit_price * Purchase.quantity))
            .group_by(Purchase.make, Purchase.model)
            .order_by(units.desc(), Purchase.make)
            .limit(limit)
        )
        return [
            TopSeller(make=make, model=model, units_sold=sold, revenue=round(money, 2))
            for make, model, sold, money in self.db.execute(query)
        ]

    def _by_category(self) -> list[CategoryCount]:
        query = (
            select(Vehicle.category, func.count(Vehicle.id), func.sum(Vehicle.quantity))
            .group_by(Vehicle.category)
            .order_by(Vehicle.category)
        )
        return [CategoryCount(category=name, models=count, units=units) for name, count, units in self.db.execute(query)]
