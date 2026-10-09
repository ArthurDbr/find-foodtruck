from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    trucks: Mapped[list["FoodTruck"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class FoodTruck(Base):
    __tablename__ = "food_trucks"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    cuisine: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped[User] = relationship(back_populates="trucks")
    stops: Mapped[list["Stop"]] = relationship(
        back_populates="truck", cascade="all, delete-orphan", order_by="Stop.day_of_week"
    )


class Stop(Base):
    """A weekly recurring location: where a truck is on a given day of the week."""

    __tablename__ = "stops"
    __table_args__ = (CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_stop_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    truck_id: Mapped[int] = mapped_column(ForeignKey("food_trucks.id", ondelete="CASCADE"), index=True)
    # 0 = Monday ... 6 = Sunday (Python's datetime.weekday convention)
    day_of_week: Mapped[int] = mapped_column(Integer, index=True)
    start_time: Mapped[str] = mapped_column(String(5))  # "HH:MM"
    end_time: Mapped[str] = mapped_column(String(5))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str] = mapped_column(String(255), default="")
    note: Mapped[str] = mapped_column(String(255), default="")

    truck: Mapped[FoodTruck] = relationship(back_populates="stops")
