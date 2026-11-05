from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError(401, 40101, "未认证")
    payload = decode_access_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise AppError(401, 40101, "未认证") from exc
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or user.deleted_at is not None or user.status != 1:
        raise AppError(401, 40102, "用户不可用")
    if payload.get("token_version") != user.token_version:
        raise AppError(401, 40102, "用户不可用")
    return user


def ensure_owner(resource, current_user: User, request: Request | None = None, resource_type: str | None = None):
    if getattr(resource, "user_id", None) != current_user.id:
        audit_event(
            "forbidden_resource",
            trace_id=getattr(getattr(request, "state", None), "trace_id", "unknown"),
            user_id=current_user.id,
            resource_type=resource_type or type(resource).__name__,
            resource_id=getattr(resource, "id", "unknown"),
            interface=request.url.path if request else "unknown",
        )
        raise AppError(403, 40301, "无权访问该资源")
    return resource
