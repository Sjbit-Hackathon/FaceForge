import base64
import binascii

from fastapi import HTTPException, status


def ensure_base64_image(image_base64: str) -> bytes:
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        return base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid base64 image") from exc


def require_record(record: dict | None, entity: str = "record") -> dict:
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")
    return record
