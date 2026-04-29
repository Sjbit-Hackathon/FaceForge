from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.models.schemas import SessionCreateRequest, SessionResponse
from app.services.supabase_service import supabase_service
from app.utils.validators import require_record

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/create", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, current_user: CurrentUser) -> SessionResponse:
    now = datetime.now(timezone.utc).isoformat()
    session = supabase_service.create_session(
        {
            "id": supabase_service.new_id(),
            "case_number": payload.case_number,
            "title": payload.title,
            "witness_name": payload.witness_name,
            "notes": payload.notes,
            "status": "active",
            "owner_user_id": current_user["id"],
            "created_at": now,
            "updated_at": now,
        }
    )
    supabase_service.log_audit(current_user["id"], "session.create", "session", session["id"], {"case_number": payload.case_number})
    session["versions"] = []
    return SessionResponse(**session)

from typing import List
@router.get("", response_model=List[SessionResponse])
def get_sessions(current_user: CurrentUser) -> List[SessionResponse]:
    sessions_data = supabase_service.get_user_sessions(current_user["id"])
    for session in sessions_data:
        session["versions"] = supabase_service.get_session_versions(session["id"])
    return [SessionResponse(**s) for s in sessions_data]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, current_user: CurrentUser) -> SessionResponse:
    session = require_record(supabase_service.get_session(session_id, current_user["id"]), "session")
    session["versions"] = supabase_service.get_session_versions(session_id)
    supabase_service.log_audit(current_user["id"], "session.read", "session", session_id)
    return SessionResponse(**session)
