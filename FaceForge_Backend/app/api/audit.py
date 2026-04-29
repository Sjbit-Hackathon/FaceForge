from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser
from app.models.schemas import AuditLogResponse
from app.services.supabase_service import supabase_service

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditLogResponse])
def get_audit_logs(current_user: CurrentUser, limit: int = Query(default=100, ge=1, le=500)) -> list[AuditLogResponse]:
    logs = supabase_service.list_audit_logs(actor_user_id=current_user["id"], limit=limit)
    return [AuditLogResponse(**log) for log in logs]
