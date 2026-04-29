import base64
from io import BytesIO
from typing import Dict, Optional

from fastapi import HTTPException, status
from huggingface_hub import InferenceClient
from PIL import Image

from app.core.config import settings


class HuggingFaceService:
    def __init__(self) -> None:
        self.client = InferenceClient(token=settings.huggingface_api_token, timeout=settings.hf_timeout_seconds)

    def generate_flux_face(self, features: Dict, negative_prompt: Optional[str] = None) -> bytes:
        prompt = self._features_to_prompt(features)
        if negative_prompt:
            prompt = f"{prompt}\nAvoid: {negative_prompt}"
        return self._image_generation(settings.hf_flux_model, {"inputs": prompt, "parameters": {"num_inference_steps": 4}})

    def restore_face_codeformer(self, image_bytes: bytes) -> bytes:
        return self._image_to_image(settings.hf_codeformer_model, image_bytes, {"fidelity": 0.7})

    def upscale_realesrgan(self, image_bytes: bytes) -> bytes:
        return self._image_to_image(settings.hf_realesrgan_model, image_bytes, {"scale": 2})

    def inpaint(self, image_bytes: bytes, mask_bytes: bytes, prompt: str) -> bytes:
        payload = {
            "inputs": {
                "image": base64.b64encode(image_bytes).decode("utf-8"),
                "mask": base64.b64encode(mask_bytes).decode("utf-8"),
                "prompt": prompt,
            }
        }
        return self._post_bytes(settings.hf_inpainting_model, payload)

    def _image_generation(self, model: str, payload: Dict) -> bytes:
        return self._post_bytes(model, payload)

    def _image_to_image(self, model: str, image_bytes: bytes, parameters: Dict) -> bytes:
        payload = {"inputs": base64.b64encode(image_bytes).decode("utf-8"), "parameters": parameters}
        return self._post_bytes(model, payload)

    def _post_bytes(self, model: str, payload: Dict) -> bytes:
        try:
            result = self.client.post(json=payload, model=model)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Hugging Face request failed: {exc}") from exc
        if isinstance(result, bytes):
            return self._normalize_image(result)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Unexpected Hugging Face response from {model}")

    def _normalize_image(self, image_bytes: bytes) -> bytes:
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            output = BytesIO()
            image.save(output, format="PNG", optimize=True)
            return output.getvalue()
        except Exception:
            return image_bytes

    def _features_to_prompt(self, features: Dict) -> str:
        marks = ", ".join(features.get("marks") or [])
        return (
            "high resolution forensic facial composite, front-facing neutral expression, "
            "plain background, realistic police sketch style, "
            f"{features.get('gender')} {features.get('age')}, {features.get('skin')} skin, "
            f"{features.get('eyes')} eyes, {features.get('nose')} nose, {features.get('jaw')} jaw, "
            f"distinguishing marks: {marks or 'none'}"
        )


hf_service = HuggingFaceService()
