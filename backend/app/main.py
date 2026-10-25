from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.database import Base, build_engine, build_session_factory
from app.errors import register_error_handlers
from app.routers import auth, purchases, stats, vehicles
from app.seed import seed


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = build_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        Base.metadata.create_all(engine)
        if settings.seed_demo_data:
            with build_session_factory(engine)() as db:
                try:
                    seed(db, settings)
                except IntegrityError:
                    # another instance seeded the same rows a moment earlier
                    db.rollback()
        yield
        engine.dispose()

    app = FastAPI(title="Car Dealership Inventory API", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.session_factory = build_session_factory(engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(auth.router)
    app.include_router(vehicles.router)
    app.include_router(purchases.router)
    app.include_router(stats.router)

    @app.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app
