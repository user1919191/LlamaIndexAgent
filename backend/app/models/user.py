from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username_normalized", name="uk_users_username_normalized"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    username_normalized: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    school: Mapped[str | None] = mapped_column(String(128), nullable=True)
    major: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def public_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email,
            "school": self.school,
            "major": self.major,
        }
