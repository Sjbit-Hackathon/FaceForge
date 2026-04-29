from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class UserRecord:
    id: str
    email: str
    password_hash: str
    full_name: str
    badge_id: str
    role: str


@dataclass
class SessionRecord:
    id: str
    case_number: str
    title: str
    status: str
    owner_user_id: str
    created_at: datetime


@dataclass
class VersionRecord:
    id: str
    session_id: str
    image_path: str
    image_hash: str
    features: Dict[str, Any]
    prompt: str
    created_at: datetime


@dataclass
class AuditRecord:
    id: str
    actor_user_id: str
    action: str
    entity_type: str
    entity_id: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
