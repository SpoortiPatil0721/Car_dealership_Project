import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

ENTRY = Path(__file__).resolve().parents[2] / "api" / "index.py"


def load_entry(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'vercel.db'}")
    monkeypatch.setenv("SEED_DEMO_DATA", "true")
    spec = importlib.util.spec_from_file_location("vercel_entry", ENTRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vercel_entry_exposes_a_working_app(monkeypatch, tmp_path):
    module = load_entry(monkeypatch, tmp_path)
    with TestClient(module.app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}
        login = client.post("/api/auth/login", json={"email": "admin@dealership.com", "password": "admin123"})
        assert login.status_code == 200


def test_startup_survives_a_seeding_race(monkeypatch, tmp_path):
    # two cold starts on vercel can seed the same database at the same moment
    from sqlalchemy.exc import IntegrityError

    import app.main

    def lose_the_race(db, settings):
        raise IntegrityError("insert", {}, Exception("duplicate email"))

    monkeypatch.setattr(app.main, "seed", lose_the_race)
    module = load_entry(monkeypatch, tmp_path)
    with TestClient(module.app) as client:
        assert client.get("/api/health").status_code == 200
