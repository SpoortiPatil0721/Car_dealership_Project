import os
from dataclasses import dataclass, field


def _split_csv(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def _normalize_db_url(url: str) -> str:
    # render and heroku hand out postgres:// which sqlalchemy no longer accepts
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./dealership.db"
    jwt_secret: str = "dev-only-secret-change-me-before-deploying"
    jwt_algorithm: str = "HS256"
    token_minutes: int = 120
    password_iterations: int = 310_000
    admin_emails: tuple[str, ...] = ()
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)
    low_stock_threshold: int = 2
    seed_demo_data: bool = False
    seed_password: str = "admin123"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=_normalize_db_url(os.getenv("DATABASE_URL", cls.database_url)),
            jwt_secret=os.getenv("JWT_SECRET", cls.jwt_secret),
            token_minutes=int(os.getenv("TOKEN_MINUTES", cls.token_minutes)),
            admin_emails=tuple(e.lower() for e in _split_csv(os.getenv("ADMIN_EMAILS", ""))),
            cors_origins=_split_csv(os.getenv("CORS_ORIGINS", ",".join(cls.cors_origins))),
            low_stock_threshold=int(os.getenv("LOW_STOCK_THRESHOLD", cls.low_stock_threshold)),
            seed_demo_data=os.getenv("SEED_DEMO_DATA", "").lower() in ("1", "true", "yes"),
            seed_password=os.getenv("SEED_PASSWORD", cls.seed_password),
        )
