from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.dependencies import CurrentUser
from app.models.schemas import FaceForgeResponse, RefineRequest
from app.services.hf_service import hf_service
from app.services.image_service import image_service
from app.services.supabase_service import supabase_service
from app.utils.validators import require_record

router = APIRouter(tags=["refine"])


@router.post("/refine", response_model=FaceForgeResponse)
def refine_face(payload: RefineRequest, current_user: CurrentUser) -> FaceForgeResponse:
    require_record(supabase_service.get_session(payload.session_id, current_user["id"]), "session")
    source = require_record(supabase_service.get_version(payload.version_id, payload.session_id), "version")
    source_image = image_service.load_image(source["image_path"])
    mask = image_service.generate_refinement_mask(source_image)
    refined = hf_service.inpaint(source_image, mask, payload.refinement_prompt)
    restored = hf_service.restore_face_codeformer(refined)
    upscaled = hf_service.upscale_realesrgan(restored)
    new_version_id = supabase_service.new_id()
    image_path, image_url, image_hash = image_service.save_image(payload.session_id, new_version_id, upscaled)
    timestamp = datetime.now(timezone.utc)
    features = source.get("features") or {}
    supabase_service.create_version(
        {
            "id": new_version_id,
            "session_id": payload.session_id,
            "version_label": "v3",
            "parent_version_id": payload.version_id,
            "prompt": payload.refinement_prompt,
            "features": features,
            "image_path": image_path,
            "image_hash": image_hash,
            "created_by": current_user["id"],
            "created_at": timestamp.isoformat(),
        }
    )
    supabase_service.log_audit(
        current_user["id"],
        "ai.refine",
        "version",
        new_version_id,
        {"session_id": payload.session_id, "parent_version_id": payload.version_id, "mask": "opencv-canny-dilate"},
    )
    return FaceForgeResponse(version_id="v3", image_url=image_url, features=features, hash=image_hash, timestamp=timestamp)
