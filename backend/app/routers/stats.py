from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import Settings
from app.deps import get_db, get_settings, require_admin
from app.schemas import StatsSummary
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"], dependencies=[Depends(require_admin)])


@router.get("/summary", response_model=StatsSummary)
def summary(db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    return StatsService(db, settings.low_stock_threshold).summary()
