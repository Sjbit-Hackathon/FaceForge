from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.models.schemas import ExportRequest
from app.services.pdf_service import pdf_service
from app.services.supabase_service import supabase_service
from app.utils.validators import require_record

router = APIRouter(tags=["export"])


@router.post("/export")
def export_report(payload: ExportRequest, current_user: CurrentUser) -> dict:
    session = require_record(supabase_service.get_session(payload.session_id, current_user["id"]), "session")
    versions = supabase_service.get_session_versions(payload.session_id)
    audit_logs = supabase_service.list_audit_logs(current_user["id"]) if payload.include_audit else []
    pdf_bytes = pdf_service.build_case_report(session, versions, audit_logs)
    report_path, report_url = pdf_service.save_report(payload.session_id, pdf_bytes)
    supabase_service.log_audit(
        current_user["id"],
        "report.export",
        "session",
        payload.session_id,
        {"report_path": report_path, "version_count": len(versions)},
    )
    return {"report_url": report_url, "report_path": report_path, "session_id": payload.session_id}
