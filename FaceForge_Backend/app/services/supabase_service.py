from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException, status
from supabase import Client, create_client

from app.core.config import settings


class SupabaseService:
    def __init__(self) -> None:
        self.client: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        self.images_bucket = settings.supabase_images_bucket
        self.reports_bucket = settings.supabase_reports_bucket

    def create_user(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            existing = self.client.table("users").select("*").eq("email", payload["email"]).limit(1).execute()
            if existing.data:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
            response = self.client.table("users").insert(payload).execute()
            return response.data[0]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        response = self.client.table("users").select("*").eq("email", email).limit(1).execute()
        return response.data[0] if response.data else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        response = self.client.table("users").select("*").eq("id", user_id).limit(1).execute()
        return response.data[0] if response.data else None

    def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.table("sessions").insert(payload).execute()
        return response.data[0]

    def get_session(self, session_id: str, owner_user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = self.client.table("sessions").select("*").eq("id", session_id).limit(1)
        if owner_user_id:
            query = query.eq("owner_user_id", owner_user_id)
        response = query.execute()
        return response.data[0] if response.data else None

    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        response = self.client.table("sessions").select("*").eq("owner_user_id", user_id).order("created_at", desc=True).execute()
        return response.data or []

    def get_session_versions(self, session_id: str) -> List[Dict[str, Any]]:
        response = (
            self.client.table("versions")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def create_version(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.table("versions").insert(payload).execute()
        return response.data[0]

    def get_version(self, version_id: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = self.client.table("versions").select("*").eq("id", version_id).limit(1)
        if session_id:
            query = query.eq("session_id", session_id)
        response = query.execute()
        return response.data[0] if response.data else None

    def upload_private_object(self, bucket: str, path: str, payload: bytes, content_type: str) -> str:
        self.client.storage.from_(bucket).upload(
            path,
            payload,
            file_options={"content-type": content_type, "x-upsert": "true"},
        )
        return path

    def create_signed_url(self, bucket: str, path: str) -> str:
        response = self.client.storage.from_(bucket).create_signed_url(path, settings.signed_url_ttl_seconds)
        return response.get("signedURL") or response.get("signedUrl") or response.get("signed_url")

    def download_private_object(self, bucket: str, path: str) -> bytes:
        return self.client.storage.from_(bucket).download(path)

    def log_audit(
        self,
        actor_user_id: str,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "id": str(uuid4()),
            "actor_user_id": actor_user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self.client.table("audit_logs").insert(payload).execute()
        return response.data[0]

    def list_audit_logs(self, actor_user_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = self.client.table("audit_logs").select("*").order("created_at", desc=True).limit(limit)
        if actor_user_id:
            query = query.eq("actor_user_id", actor_user_id)
        response = query.execute()
        return response.data or []

    def new_id(self) -> str:
        return str(uuid4())


supabase_service = SupabaseService()
