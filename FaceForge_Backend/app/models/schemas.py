from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RegisterRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    full_name: str
    badge_id: str
    role: str = "OFFICER"


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str


class SessionCreateRequest(BaseModel):
    case_number: str
    title: str
    witness_name: Optional[str] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    case_number: str
    title: str
    status: str
    witness_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    versions: List[Dict[str, Any]] = []


class GenerateRequest(BaseModel):
    session_id: str
    witness_description: str = Field(min_length=10)
    negative_prompt: Optional[str] = None


class RefineRequest(BaseModel):
    session_id: str
    version_id: str
    refinement_prompt: str = Field(min_length=4)
    mask_hint: Optional[str] = None


class MatchRequest(BaseModel):
    session_id: str
    version_id: Optional[str] = None
    candidate_hash: Optional[str] = None
    candidate_image_base64: Optional[str] = None
    candidate_embedding: Optional[List[float]] = None
    threshold: float = Field(default=0.92, ge=0.0, le=1.0)


class MatchResponse(BaseModel):
    match: bool
    score: float
    compared_hash: str
    target_hash: str
    method: str


class ExportRequest(BaseModel):
    session_id: str
    include_audit: bool = True


class AuditLogResponse(BaseModel):
    id: str
    actor_user_id: str
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime


class FaceFeatures(BaseModel):
    age: str
    gender: str
    skin: str
    eyes: str
    nose: str
    jaw: str
    marks: List[str] = []


class FaceForgeResponse(BaseModel):
    version_id: str
    image_url: str
    features: Dict[str, Any]
    hash: str
    timestamp: datetime
