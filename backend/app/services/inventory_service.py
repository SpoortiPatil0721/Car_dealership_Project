from sqlalchemy import update
from sqlalchemy.orm import Session

from app.errors import NotFoundError, OutOfStockError
from app.models import Purchase, User, Vehicle


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def purchase(self, vehicle_id: int, quantity: int, buyer: User) -> Vehicle:
        # the stock check lives inside the UPDATE so two buyers cannot both get the last car
        result = self.db.execute(
            update(Vehicle)
            .where(Vehicle.id == vehicle_id, Vehicle.quantity >= quantity)
            .values(quantity=Vehicle.quantity - quantity)
        )
        if result.rowcount == 0:
            vehicle = self._get(vehicle_id)
            raise OutOfStockError(f"Not enough stock, only {vehicle.quantity} left")
        vehicle = self._get(vehicle_id)
        self.db.add(
            Purchase(
                user_id=buyer.id,
                vehicle_id=vehicle.id,
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                quantity=quantity,
                unit_price=vehicle.price,
            )
        )
        self.db.commit()
        return vehicle

    def restock(self, vehicle_id: int, quantity: int) -> Vehicle:
        self._get(vehicle_id)
        self.db.execute(update(Vehicle).where(Vehicle.id == vehicle_id).values(quantity=Vehicle.quantity + quantity))
        self.db.commit()
        return self._get(vehicle_id)

    def _get(self, vehicle_id: int) -> Vehicle:
        vehicle = self.db.get(Vehicle, vehicle_id, populate_existing=True)
        if vehicle is None:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        return vehicle
