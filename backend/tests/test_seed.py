from dataclasses import replace

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import seed as seed_module
from app.main import create_app
from app.models import User, Vehicle
from app.seed import DEMO_VEHICLES, seed


def test_seed_creates_admin_demo_user_and_cars(client, settings):
    with client.app.state.session_factory() as db:
        seed(db, replace(settings, seed_password="pass1234"))
    login = client.post("/api/auth/login", json={"email": "admin@dealership.com", "password": "pass1234"})
    assert login.status_code == 200
    assert login.json()["user"]["is_admin"] is True
    with client.app.state.session_factory() as db:
        assert db.scalar(select(func.count(Vehicle.id))) == len(DEMO_VEHICLES)


def test_seed_can_run_twice_without_duplicates(client, settings):
    with client.app.state.session_factory() as db:
        seed(db, settings)
        seed(db, settings)
        assert db.scalar(select(func.count(Vehicle.id))) == len(DEMO_VEHICLES)
        assert db.scalar(select(func.count(User.id))) == 2


def test_app_seeds_itself_when_flag_is_on(settings):
    with TestClient(create_app(replace(settings, seed_demo_data=True))) as seeded:
        login = seeded.post("/api/auth/login", json={"email": "demo@dealership.com", "password": "admin123"})
        assert login.status_code == 200


def test_seed_script_entry_point(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'cli.db'}")
    seed_module.main()
    assert "Seed done" in capsys.readouterr().out
