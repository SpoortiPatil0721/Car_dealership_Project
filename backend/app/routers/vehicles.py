from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, require_admin
from app.models import User
from app.schemas import PurchaseRequest, RestockRequest, VehicleCreate, VehicleOut, VehicleSearch, VehicleUpdate
from app.services.inventory_service import InventoryService
from app.services.vehicle_service import VehicleService

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


def get_vehicle_service(db: Session = Depends(get_db)) -> VehicleService:
    return VehicleService(db)


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    return InventoryService(db)


@router.get("", response_model=list[VehicleOut], dependencies=[Depends(get_current_user)])
def list_vehicles(service: VehicleService = Depends(get_vehicle_service)):
    return service.list_all()


@router.get("/search", response_model=list[VehicleOut], dependencies=[Depends(get_current_user)])
def search_vehicles(
    filters: Annotated[VehicleSearch, Query()],
    service: VehicleService = Depends(get_vehicle_service),
):
    return service.search(filters)


@router.get("/categories", response_model=list[str], dependencies=[Depends(get_current_user)])
def list_categories(service: VehicleService = Depends(get_vehicle_service)):
    return service.categories()


@router.get("/{vehicle_id}", response_model=VehicleOut, dependencies=[Depends(get_current_user)])
def get_vehicle(vehicle_id: int, service: VehicleService = Depends(get_vehicle_service)):
    return service.get(vehicle_id)


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def add_vehicle(data: VehicleCreate, service: VehicleService = Depends(get_vehicle_service)):
    return service.create(data)


@router.put("/{vehicle_id}", response_model=VehicleOut, dependencies=[Depends(require_admin)])
def update_vehicle(vehicle_id: int, data: VehicleUpdate, service: VehicleService = Depends(get_vehicle_service)):
    return service.update(vehicle_id, data)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_vehicle(vehicle_id: int, service: VehicleService = Depends(get_vehicle_service)):
    service.delete(vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vehicle_id}/purchase", response_model=VehicleOut)
def purchase_vehicle(
    vehicle_id: int,
    data: PurchaseRequest | None = None,
    user: User = Depends(get_current_user),
    inventory: InventoryService = Depends(get_inventory_service),
):
    quantity = data.quantity if data else 1
    return inventory.purchase(vehicle_id, quantity, buyer=user)


@router.post("/{vehicle_id}/restock", response_model=VehicleOut, dependencies=[Depends(require_admin)])
def restock_vehicle(vehicle_id: int, data: RestockRequest, inventory: InventoryService = Depends(get_inventory_service)):
    return inventory.restock(vehicle_id, data.quantity)
