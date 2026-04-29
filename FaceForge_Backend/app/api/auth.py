from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.services.supabase_service import supabase_service
from app.utils.hashing import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> TokenResponse:
    user = supabase_service.create_user(
        {
            "id": supabase_service.new_id(),
            "email": payload.email.lower(),
            "password_hash": hash_password(payload.password),
            "full_name": payload.full_name,
            "badge_id": payload.badge_id,
            "role": payload.role,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    supabase_service.log_audit(user["id"], "auth.register", "user", user["id"], {"email": user["email"]})
    token = create_access_token(data={"sub": str(user["id"]), "role": user.get("role"), "email": user["email"]})
    safe_user = {key: value for key, value in user.items() if key != "password_hash"}
    return TokenResponse(access_token=token, user=safe_user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = supabase_service.get_user_by_email(payload.email.lower())
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    supabase_service.log_audit(user["id"], "auth.login", "user", user["id"], {"email": user["email"]})
    token = create_access_token(data={"sub": str(user["id"]), "role": user.get("role"), "email": user["email"]})
    safe_user = {key: value for key, value in user.items() if key != "password_hash"}
    return TokenResponse(access_token=token, user=safe_user)
