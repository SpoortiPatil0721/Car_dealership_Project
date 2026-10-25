from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db, require_admin
from app.models import User
from app.schemas import PurchaseOut, SaleOut
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


def get_purchase_service(db: Session = Depends(get_db)) -> PurchaseService:
    return PurchaseService(db)


@router.get("/me", response_model=list[PurchaseOut])
def my_purchases(user: User = Depends(get_current_user), service: PurchaseService = Depends(get_purchase_service)):
    return service.for_user(user)


@router.get("", response_model=list[SaleOut], dependencies=[Depends(require_admin)])
def all_sales(service: PurchaseService = Depends(get_purchase_service)):
    return service.all_sales()
