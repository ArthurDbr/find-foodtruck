import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..models import FoodTruck, Stop
from ..schemas import StopWithTruck

router = APIRouter(prefix="/api/stops", tags=["stops"])


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@router.get("", response_model=list[StopWithTruck])
def search_stops(
    day: int | None = Query(None, ge=0, le=6, description="0 = Monday ... 6 = Sunday"),
    q: str | None = Query(None, max_length=100, description="Match truck name, cuisine or address"),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Stop).join(Stop.truck).options(joinedload(Stop.truck))
    if day is not None:
        stmt = stmt.where(Stop.day_of_week == day)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(FoodTruck.name.ilike(like), FoodTruck.cuisine.ilike(like), Stop.address.ilike(like))
        )
    stmt = stmt.order_by(Stop.day_of_week, Stop.start_time)

    results = []
    for stop in db.scalars(stmt).unique():
        item = StopWithTruck.model_validate(stop)
        if lat is not None and lng is not None:
            item.distance_km = round(haversine_km(lat, lng, stop.latitude, stop.longitude), 2)
            if radius_km is not None and item.distance_km > radius_km:
                continue
        results.append(item)
    if lat is not None and lng is not None:
        results.sort(key=lambda s: s.distance_km)
    return results
