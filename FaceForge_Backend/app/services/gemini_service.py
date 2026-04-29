import json
from typing import Any, Dict

import google.generativeai as genai
from fastapi import HTTPException, status

from app.core.config import settings


class GeminiService:
    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def structure_description(self, description: str) -> Dict[str, Any]:
        prompt = f"""
You are a forensic composite assistant. Convert the witness statement into strict JSON.
Return only JSON with these keys: age, gender, skin, eyes, nose, jaw, marks.
Use concise forensic descriptors. marks must be an array of strings.

Witness statement:
{description}
"""
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
        )
        try:
            parsed = json.loads(response.text)
        except (TypeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned non-JSON feature output",
            ) from exc
        required = {"age", "gender", "skin", "eyes", "nose", "jaw", "marks"}
        missing = required.difference(parsed)
        if missing:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Gemini response missing: {missing}")
        if not isinstance(parsed.get("marks"), list):
            parsed["marks"] = [str(parsed["marks"])]
        return parsed


gemini_service = GeminiService()
