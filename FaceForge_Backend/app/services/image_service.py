import base64
from io import BytesIO
from typing import Tuple

import cv2
import numpy as np
from PIL import Image, ImageOps

from app.services.supabase_service import supabase_service
from app.utils.hashing import sha256_bytes


class ImageService:
    def image_to_base64(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")

    def base64_to_image(self, image_base64: str) -> bytes:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        return base64.b64decode(image_base64)

    def fingerprint(self, image_bytes: bytes) -> str:
        normalized = self.normalize_png(image_bytes)
        return sha256_bytes(normalized)

    def normalize_png(self, image_bytes: bytes) -> bytes:
        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image).convert("RGB")
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    def generate_refinement_mask(self, image_bytes: bytes) -> bytes:
        image = np.array(Image.open(BytesIO(image_bytes)).convert("RGB"))
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((9, 9), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            pad_x, pad_y = int(w * 0.08), int(h * 0.08)
            cv2.rectangle(
                mask,
                (max(0, x - pad_x), max(0, y - pad_y)),
                (min(mask.shape[1], x + w + pad_x), min(mask.shape[0], y + h + pad_y)),
                255,
                -1,
            )
        else:
            h, w = gray.shape
            cv2.ellipse(mask, (w // 2, h // 2), (w // 3, h // 2), 0, 0, 360, 255, -1)
        _, encoded = cv2.imencode(".png", mask)
        return encoded.tobytes()

    def save_image(self, session_id: str, version_id: str, image_bytes: bytes) -> Tuple[str, str, str]:
        normalized = self.normalize_png(image_bytes)
        image_hash = sha256_bytes(normalized)
        path = f"{session_id}/{version_id}.png"
        supabase_service.upload_private_object(supabase_service.images_bucket, path, normalized, "image/png")
        signed_url = supabase_service.create_signed_url(supabase_service.images_bucket, path)
        return path, signed_url, image_hash

    def load_image(self, path: str) -> bytes:
        return supabase_service.download_private_object(supabase_service.images_bucket, path)


image_service = ImageService()
