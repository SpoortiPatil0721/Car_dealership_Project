import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED_VEHICLE_FIELDS = ("make", "model", "category", "price", "quantity")


class StrictModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class Credentials(StrictModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("enter a valid email address")
        return value.lower()


class RegisterRequest(Credentials):
    full_name: str = Field(min_length=1, max_length=120)


class LoginRequest(Credentials):
    pass


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_admin: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class VehicleFields(StrictModel):
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    category: str = Field(min_length=1, max_length=40)
    price: float = Field(gt=0, le=100_000_000)
    quantity: int = Field(ge=0, le=100_000)
    year: int | None = Field(default=None, ge=1886, le=2100)
    color: str | None = Field(default=None, max_length=40)
    image_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=2000)


class VehicleCreate(VehicleFields):
    pass


class VehicleUpdate(StrictModel):
    make: str | None = Field(default=None, min_length=1, max_length=60)
    model: str | None = Field(default=None, min_length=1, max_length=60)
    category: str | None = Field(default=None, min_length=1, max_length=40)
    price: float | None = Field(default=None, gt=0, le=100_000_000)
    quantity: int | None = Field(default=None, ge=0, le=100_000)
    year: int | None = Field(default=None, ge=1886, le=2100)
    color: str | None = Field(default=None, max_length=40)
    image_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def check_changes(self):
        changes = self.model_dump(exclude_unset=True)
        if not changes:
            raise ValueError("send at least one field to update")
        for required in REQUIRED_VEHICLE_FIELDS:
            if required in changes and changes[required] is None:
                raise ValueError(f"{required} cannot be empty")
        return self


class VehicleOut(VehicleFields):
    model_config = ConfigDict(from_attributes=True)

    id: int


SortOption = Literal["name", "price_asc", "price_desc", "newest", "stock_desc"]


class VehicleSearch(StrictModel):
    make: str | None = None
    model: str | None = None
    category: str | None = None
    q: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    in_stock: bool = False
    sort: SortOption = "name"


class PurchaseRequest(StrictModel):
    quantity: int = Field(default=1, ge=1, le=100)


class RestockRequest(StrictModel):
    quantity: int = Field(ge=1, le=10_000)


class PurchaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int | None
    make: str
    model: str
    year: int | None
    quantity: int
    unit_price: float
    total_price: float
    purchased_at: datetime


class SaleOut(PurchaseOut):
    buyer_email: str


class LowStockItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    make: str
    model: str
    quantity: int


class TopSeller(BaseModel):
    make: str
    model: str
    units_sold: int
    revenue: float


class CategoryCount(BaseModel):
    category: str
    models: int
    units: int


class StatsSummary(BaseModel):
    total_models: int
    units_in_stock: int
    inventory_value: float
    out_of_stock: int
    units_sold: int
    revenue: float
    low_stock: list[LowStockItem]
    top_sellers: list[TopSeller]
    by_category: list[CategoryCount]
