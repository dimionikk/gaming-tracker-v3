from app.database import Base
from uuid import UUID, uuid4
from sqlalchemy import UUID as SUUID, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(SUUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[UUID] = mapped_column(SUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)