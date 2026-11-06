from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.audit import audit_event
from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas import ChangePasswordRequest, ProfileUpdateRequest


router = APIRouter(prefix="/users", tags=["users"])


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"code": 0, "message": "ok", "data": {"user": current_user.public_dict()}}


@router.patch("/me")
def update_me(
    payload: ProfileUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fields = list(payload.model_fields_set)
    for field in fields:
        setattr(current_user, field, getattr(payload, field))
    if fields:
        db.commit()
        db.refresh(current_user)
        audit_event("profile_update", trace_id=request.state.trace_id, user_id=current_user.id, fields=",".join(sorted(fields)), result_code=0)
    return {"code": 0, "message": "ok", "data": {"user": current_user.public_dict()}}


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        audit_event("password_change", trace_id=request.state.trace_id, user_id=current_user.id, ip=client_ip(request), result_code=42201)
        raise AppError(422, 42201, "原密码错误")
    current_user.password_hash = hash_password(payload.new_password)
    current_user.token_version += 1
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    audit_event("password_change", trace_id=request.state.trace_id, user_id=current_user.id, ip=client_ip(request), result_code=0)
    return None
