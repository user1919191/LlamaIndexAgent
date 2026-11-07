from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import audit_event, audit_login
from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, normalize_username, username_digest, verify_password
from app.db import get_db
from app.models.user import User
from app.schemas import LoginRequest, RegisterRequest


router = APIRouter(prefix="/auth", tags=["auth"])


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    normalized = normalize_username(payload.username)
    digest = username_digest(normalized)
    existing = db.scalar(select(User).where(User.username_normalized == normalized))
    if existing is not None:
        audit_event("register", trace_id=request.state.trace_id, username_digest=digest, ip=client_ip(request), result_code=40901)
        raise AppError(409, 40901, "用户名已存在")
    user = User(
        username=payload.username,
        username_normalized=normalized,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        email=payload.email,
        school=payload.school,
        major=payload.major,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        audit_event("register", trace_id=request.state.trace_id, username_digest=digest, ip=client_ip(request), result_code=40901)
        raise AppError(409, 40901, "用户名已存在") from exc
    db.refresh(user)
    audit_event("register", trace_id=request.state.trace_id, username_digest=digest, ip=client_ip(request), result_code=0)
    return {"code": 0, "message": "registered", "data": {"user": user.public_dict()}}


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    normalized = normalize_username(payload.username)
    user = db.scalar(select(User).where(User.username_normalized == normalized))
    if user is None or not verify_password(payload.password, user.password_hash if user else None):
        audit_login()
        raise AppError(401, 40101, "用户名或密码错误")
    if user.deleted_at is not None or user.status != 1:
        audit_login()
        raise AppError(401, 40102, "用户不可用")
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    token, expires_at = create_access_token(user.id, user.username, user.token_version)
    audit_login()
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 7 * 24 * 60 * 60,
            "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
            "user": user.public_dict(),
        },
    }
