from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.orm import Session

from app.errors import BadRequestError, NotFoundError
from app.models import Purchase, Vehicle
from app.schemas import VehicleCreate, VehicleSearch, VehicleUpdate

SORT_ORDERS = {
    "name": (Vehicle.make, Vehicle.model),
    "price_asc": (Vehicle.price.asc(), Vehicle.id),
    "price_desc": (Vehicle.price.desc(), Vehicle.id),
    "newest": (Vehicle.created_at.desc(), Vehicle.id.desc()),
    "stock_desc": (Vehicle.quantity.desc(), Vehicle.id),
}


def apply_filters(query: Select, filters: VehicleSearch) -> Select:
    if filters.make:
        query = query.where(Vehicle.make.icontains(filters.make, autoescape=True))
    if filters.model:
        query = query.where(Vehicle.model.icontains(filters.model, autoescape=True))
    if filters.category:
        query = query.where(func.lower(Vehicle.category) == filters.category.lower())
    if filters.q:
        text_columns = (Vehicle.make, Vehicle.model, Vehicle.category)
        query = query.where(or_(*(column.icontains(filters.q, autoescape=True) for column in text_columns)))
    if filters.min_price is not None:
        query = query.where(Vehicle.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Vehicle.price <= filters.max_price)
    if filters.in_stock:
        query = query.where(Vehicle.quantity > 0)
    return query


class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Vehicle]:
        return list(self.db.scalars(select(Vehicle).order_by(*SORT_ORDERS["name"])))

    def search(self, filters: VehicleSearch) -> list[Vehicle]:
        if filters.min_price is not None and filters.max_price is not None and filters.min_price > filters.max_price:
            raise BadRequestError("min_price cannot be bigger than max_price")
        query = apply_filters(select(Vehicle), filters).order_by(*SORT_ORDERS[filters.sort])
        return list(self.db.scalars(query))

    def categories(self) -> list[str]:
        return list(self.db.scalars(select(Vehicle.category).distinct().order_by(Vehicle.category)))

    def get(self, vehicle_id: int) -> Vehicle:
        vehicle = self.db.get(Vehicle, vehicle_id)
        if vehicle is None:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")
        return vehicle

    def create(self, data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**data.model_dump())
        self.db.add(vehicle)
        self.db.commit()
        return vehicle

    def update(self, vehicle_id: int, data: VehicleUpdate) -> Vehicle:
        vehicle = self.get(vehicle_id)
        # only touch the fields the client actually sent
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(vehicle, field, value)
        self.db.commit()
        return vehicle

    def delete(self, vehicle_id: int) -> None:
        vehicle = self.get(vehicle_id)
        # sqlite ignores ON DELETE unless foreign keys are switched on, so unlink history by hand
        self.db.execute(update(Purchase).where(Purchase.vehicle_id == vehicle_id).values(vehicle_id=None))
        self.db.delete(vehicle)
        self.db.commit()
