from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import AuthenticationError, ConflictError
from app.models import User
from app.schemas import LoginRequest, RegisterRequest
from app.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    def register(self, data: RegisterRequest) -> tuple[User, str]:
        if self.db.scalar(select(User).where(User.email == data.email)):
            raise ConflictError("That email is already registered")
        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password, self.settings),
            is_admin=data.email in self.settings.admin_emails,
        )
        self.db.add(user)
        self.db.commit()
        return user, self._token_for(user)

    def login(self, data: LoginRequest) -> tuple[User, str]:
        user = self.db.scalar(select(User).where(User.email == data.email))
        # same message for both cases so nobody can probe which emails exist
        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Wrong email or password")
        return user, self._token_for(user)

    def _token_for(self, user: User) -> str:
        return create_access_token(user.id, user.is_admin, self.settings)
