"""Populate the database with demo data: `python -m app.seed`."""

from sqlalchemy import select

from .auth import hash_password
from .db import Base, SessionLocal, engine
from .models import FoodTruck, Stop, User

DEMO = [
    ("Taco Loco", "Mexican", "Tacos al pastor and fresh salsas.", [
        (0, "11:30", "14:00", 48.8566, 2.3522, "Hôtel de Ville, Paris"),
        (2, "11:30", "14:00", 48.8738, 2.2950, "Arc de Triomphe, Paris"),
        (5, "18:00", "23:00", 48.8867, 2.3431, "Montmartre, Paris"),
        (6, "12:00", "16:00", 48.8462, 2.3371, "Jardin du Luxembourg, Paris"),
    ]),
    ("Burger Bros", "Burgers", "Smash burgers & hand-cut fries.", [
        (1, "11:30", "14:30", 48.8606, 2.3376, "Louvre, Paris"),
        (4, "18:30", "22:30", 48.8529, 2.3699, "Bastille, Paris"),
        (5, "12:00", "15:00", 48.8399, 2.3770, "Gare de Lyon, Paris"),
    ]),
    ("Green Bowl", "Vegan", "Seasonal vegan bowls.", [
        (3, "11:30", "14:00", 48.8323, 2.3561, "Place d'Italie, Paris"),
        (6, "10:00", "15:00", 48.8635, 2.3768, "Marché des Enfants Rouges, Paris"),
    ]),
]


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == "demo@foodtruck.dev")):
            print("Demo data already present.")
            return
        user = User(email="demo@foodtruck.dev", password_hash=hash_password("demo1234"))
        db.add(user)
        for name, cuisine, desc, stops in DEMO:
            truck = FoodTruck(owner=user, name=name, cuisine=cuisine, description=desc)
            truck.stops = [
                Stop(day_of_week=d, start_time=s, end_time=e, latitude=lat, longitude=lng, address=addr)
                for d, s, e, lat, lng, addr in stops
            ]
            db.add(truck)
        db.commit()
        print("Seeded demo data. Login: demo@foodtruck.dev / demo1234")


if __name__ == "__main__":
    main()
