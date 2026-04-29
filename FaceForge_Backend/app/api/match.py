import math

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser
from app.models.schemas import MatchRequest, MatchResponse
from app.services.image_service import image_service
from app.services.supabase_service import supabase_service
from app.utils.hashing import sha256_bytes
from app.utils.validators import ensure_base64_image, require_record

router = APIRouter(tags=["match"])


@router.post("/match", response_model=MatchResponse)
def match_face(payload: MatchRequest, current_user: CurrentUser) -> MatchResponse:
    require_record(supabase_service.get_session(payload.session_id, current_user["id"]), "session")
    versions = supabase_service.get_session_versions(payload.session_id)
    if payload.version_id:
        target = require_record(supabase_service.get_version(payload.version_id, payload.session_id), "version")
    elif versions:
        target = versions[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No versions available for matching")

    if payload.candidate_embedding:
        target_embedding = target.get("face_embedding") or target.get("embedding")
        if not target_embedding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target version has no stored embedding")
        score = _cosine_similarity(payload.candidate_embedding, target_embedding)
        compared_hash = "embedding"
        method = "cosine_embedding"
    elif payload.candidate_hash:
        compared_hash = payload.candidate_hash
        method = "sha256"
    elif payload.candidate_image_base64:
        compared_hash = sha256_bytes(image_service.normalize_png(ensure_base64_image(payload.candidate_image_base64)))
        method = "image_sha256"
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provide candidate_hash or candidate_image_base64")

    target_hash = target["image_hash"]
    if method != "cosine_embedding":
        score = 1.0 if compared_hash == target_hash else _hex_similarity(compared_hash, target_hash)
    matched = score >= payload.threshold
    supabase_service.log_audit(
        current_user["id"],
        "match.compare",
        "version",
        target["id"],
        {"score": score, "matched": matched, "method": method},
    )
    return MatchResponse(match=matched, score=score, compared_hash=compared_hash, target_hash=target_hash, method=method)


def _hex_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    length = min(len(left), len(right))
    matches = sum(1 for index in range(length) if left[index] == right[index])
    return matches / max(len(left), len(right))


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    length = min(len(left), len(right))
    if length == 0:
        return 0.0
    dot = sum(left[index] * right[index] for index in range(length))
    left_norm = math.sqrt(sum(value * value for value in left[:length]))
    right_norm = math.sqrt(sum(value * value for value in right[:length]))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (left_norm * right_norm)))
