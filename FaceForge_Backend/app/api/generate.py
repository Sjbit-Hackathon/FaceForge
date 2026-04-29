from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.models.schemas import FaceForgeResponse, GenerateRequest
from app.services.gemini_service import gemini_service
from app.services.hf_service import hf_service
from app.services.image_service import image_service
from app.services.supabase_service import supabase_service
from app.utils.validators import require_record

router = APIRouter(tags=["generate"])


@router.post("/generate", response_model=FaceForgeResponse)
def generate_face(payload: GenerateRequest, current_user: CurrentUser) -> FaceForgeResponse:
    require_record(supabase_service.get_session(payload.session_id, current_user["id"]), "session")
    features = gemini_service.structure_description(payload.witness_description)
    raw_image = hf_service.generate_flux_face(features, payload.negative_prompt)
    restored = hf_service.restore_face_codeformer(raw_image)
    upscaled = hf_service.upscale_realesrgan(restored)
    version_id = supabase_service.new_id()
    image_path, image_url, image_hash = image_service.save_image(payload.session_id, version_id, upscaled)
    timestamp = datetime.now(timezone.utc)
    supabase_service.create_version(
        {
            "id": version_id,
            "session_id": payload.session_id,
            "version_label": "v3",
            "prompt": payload.witness_description,
            "features": features,
            "image_path": image_path,
            "image_hash": image_hash,
            "created_by": current_user["id"],
            "created_at": timestamp.isoformat(),
        }
    )
    supabase_service.log_audit(
        current_user["id"],
        "ai.generate",
        "version",
        version_id,
        {"session_id": payload.session_id, "model": "Gemini + FLUX.1 + CodeFormer + Real-ESRGAN"},
    )
    return FaceForgeResponse(version_id="v3", image_url=image_url, features=features, hash=image_hash, timestamp=timestamp)
