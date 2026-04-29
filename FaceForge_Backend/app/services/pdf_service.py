from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.supabase_service import supabase_service


class PDFService:
    def build_case_report(
        self,
        session: Dict[str, Any],
        versions: List[Dict[str, Any]],
        audit_logs: List[Dict[str, Any]],
    ) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("FaceForge Forensic Composite Report", styles["Title"]),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Case: {session['case_number']} - {session['title']}", styles["Heading2"]),
            Paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}", styles["Normal"]),
            Spacer(1, 0.25 * inch),
        ]
        session_rows = [
            ["Status", session.get("status", "")],
            ["Witness", session.get("witness_name") or "Not recorded"],
            ["Notes", session.get("notes") or ""],
        ]
        story.append(self._table(session_rows))
        story.append(Spacer(1, 0.25 * inch))
        story.append(Paragraph("Composite Versions", styles["Heading2"]))
        version_rows = [["Version", "Image Hash", "Created", "Features"]]
        for version in versions:
            features = version.get("features") or {}
            feature_text = ", ".join(f"{key}: {value}" for key, value in features.items())
            version_rows.append([version["id"], version.get("image_hash", ""), version.get("created_at", ""), feature_text])
        story.append(self._table(version_rows, header=True))
        if audit_logs:
            story.append(Spacer(1, 0.25 * inch))
            story.append(Paragraph("Audit Trail", styles["Heading2"]))
            audit_rows = [["Time", "Action", "Entity", "Metadata"]]
            for log in audit_logs:
                audit_rows.append([
                    log.get("created_at", ""),
                    log.get("action", ""),
                    f"{log.get('entity_type')}:{log.get('entity_id')}",
                    str(log.get("metadata") or {}),
                ])
            story.append(self._table(audit_rows, header=True))
        doc.build(story)
        return buffer.getvalue()

    def save_report(self, session_id: str, pdf_bytes: bytes) -> Tuple[str, str]:
        path = f"{session_id}/faceforge-report.pdf"
        supabase_service.upload_private_object(supabase_service.reports_bucket, path, pdf_bytes, "application/pdf")
        return path, supabase_service.create_signed_url(supabase_service.reports_bucket, path)

    def _table(self, rows: List[List[Any]], header: bool = False) -> Table:
        table = Table(rows, repeatRows=1 if header else 0)
        style = [
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        if header:
            style.extend([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)])
        table.setStyle(TableStyle(style))
        return table


pdf_service = PDFService()
