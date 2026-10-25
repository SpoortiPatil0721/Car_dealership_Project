from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Base, build_engine, build_session_factory
from app.models import User, Vehicle
from app.security import hash_password

DEMO_VEHICLES = [
    ("Toyota", "Corolla Altis", "Sedan", 21500, 6, 2024, "Silver"),
    ("Honda", "City", "Sedan", 16800, 4, 2025, "Red"),
    ("Hyundai", "Verna", "Sedan", 17900, 1, 2024, "White"),
    ("Mahindra", "Thar", "SUV", 19500, 3, 2025, "Green"),
    ("Toyota", "Fortuner", "SUV", 46000, 2, 2024, "Black"),
    ("Kia", "Seltos", "SUV", 18200, 0, 2024, "Blue"),
    ("Tata", "Nexon EV", "Electric", 17400, 5, 2025, "Teal"),
    ("Tesla", "Model 3", "Electric", 42990, 2, 2025, "White"),
    ("Maruti Suzuki", "Swift", "Hatchback", 8200, 9, 2025, "Orange"),
    ("Volkswagen", "Polo", "Hatchback", 9800, 0, 2023, "Grey"),
    ("Ford", "Mustang GT", "Coupe", 58900, 1, 2024, "Yellow"),
    ("Toyota", "Hilux", "Pickup", 37500, 2, 2024, "Bronze"),
]

DEMO_USERS = [
    ("admin@dealership.com", "Lot Admin", True),
    ("demo@dealership.com", "Demo Buyer", False),
]


def seed(db: Session, settings: Settings) -> None:
    for email, name, is_admin in DEMO_USERS:
        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(email=email, full_name=name, is_admin=is_admin, password_hash=hash_password(settings.seed_password, settings)))
    # only add cars to an empty lot so re-running never duplicates them
    if db.scalar(select(func.count(Vehicle.id))) == 0:
        for make, model, category, price, quantity, year, color in DEMO_VEHICLES:
            db.add(Vehicle(make=make, model=model, category=category, price=price, quantity=quantity, year=year, color=color))
    db.commit()


def main() -> None:
    settings = Settings.from_env()
    engine = build_engine(settings.database_url)
    Base.metadata.create_all(engine)
    with build_session_factory(engine)() as db:
        seed(db, settings)
    engine.dispose()
    print("Seed done. Log in as admin@dealership.com or demo@dealership.com")


if __name__ == "__main__":
    main()
