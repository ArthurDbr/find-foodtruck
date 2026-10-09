from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import current_user
from ..db import get_db
from ..models import FoodTruck, Stop, User
from ..schemas import StopCreate, StopOut, TruckCreate, TruckOut

router = APIRouter(prefix="/api/trucks", tags=["trucks"])


def _owned_truck(truck_id: int, user: User, db: Session) -> FoodTruck:
    truck = db.get(FoodTruck, truck_id)
    if truck is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Truck not found")
    if truck.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not own this truck")
    return truck


@router.get("", response_model=list[TruckOut])
def list_trucks(db: Session = Depends(get_db)):
    return db.scalars(select(FoodTruck).order_by(FoodTruck.name)).all()


@router.get("/mine", response_model=list[TruckOut])
def my_trucks(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(FoodTruck).where(FoodTruck.owner_id == user.id).order_by(FoodTruck.name)).all()


@router.get("/{truck_id}", response_model=TruckOut)
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.get(FoodTruck, truck_id)
    if truck is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Truck not found")
    return truck


@router.post("", response_model=TruckOut, status_code=status.HTTP_201_CREATED)
def create_truck(body: TruckCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    truck = FoodTruck(owner_id=user.id, **body.model_dump())
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


@router.put("/{truck_id}", response_model=TruckOut)
def update_truck(
    truck_id: int, body: TruckCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    truck = _owned_truck(truck_id, user, db)
    for key, value in body.model_dump().items():
        setattr(truck, key, value)
    db.commit()
    db.refresh(truck)
    return truck


@router.delete("/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_truck(truck_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(_owned_truck(truck_id, user, db))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{truck_id}/stops", response_model=StopOut, status_code=status.HTTP_201_CREATED)
def add_stop(
    truck_id: int, body: StopCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    truck = _owned_truck(truck_id, user, db)
    stop = Stop(truck_id=truck.id, **body.model_dump())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop


@router.put("/{truck_id}/stops/{stop_id}", response_model=StopOut)
def update_stop(
    truck_id: int,
    stop_id: int,
    body: StopCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    _owned_truck(truck_id, user, db)
    stop = db.get(Stop, stop_id)
    if stop is None or stop.truck_id != truck_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stop not found")
    for key, value in body.model_dump().items():
        setattr(stop, key, value)
    db.commit()
    db.refresh(stop)
    return stop


@router.delete("/{truck_id}/stops/{stop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stop(
    truck_id: int, stop_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    _owned_truck(truck_id, user, db)
    stop = db.get(Stop, stop_id)
    if stop is None or stop.truck_id != truck_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stop not found")
    db.delete(stop)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
