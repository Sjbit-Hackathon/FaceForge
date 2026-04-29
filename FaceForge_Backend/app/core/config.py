import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    api_prefix: str
    cors_origins: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    gemini_api_key: str
    gemini_model: str
    huggingface_api_token: str
    hf_flux_model: str
    hf_codeformer_model: str
    hf_realesrgan_model: str
    hf_inpainting_model: str
    hf_timeout_seconds: int
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_images_bucket: str
    supabase_reports_bucket: str
    signed_url_ttl_seconds: int

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "FaceForge API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        api_prefix=os.getenv("API_PREFIX", ""),
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"),
        jwt_secret=_env("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")),
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        huggingface_api_token=_env("HUGGINGFACE_API_TOKEN"),
        hf_flux_model=os.getenv("HF_FLUX_MODEL", "black-forest-labs/FLUX.1-schnell"),
        hf_codeformer_model=os.getenv("HF_CODEFORMER_MODEL", "sczhou/CodeFormer"),
        hf_realesrgan_model=os.getenv("HF_REALESRGAN_MODEL", "ai-forever/Real-ESRGAN"),
        hf_inpainting_model=os.getenv("HF_INPAINTING_MODEL", "stabilityai/stable-diffusion-2-inpainting"),
        hf_timeout_seconds=int(os.getenv("HF_TIMEOUT_SECONDS", "120")),
        supabase_url=_env("SUPABASE_URL"),
        supabase_anon_key=_env("SUPABASE_ANON_KEY"),
        supabase_service_role_key=_env("SUPABASE_SERVICE_ROLE_KEY"),
        supabase_images_bucket=os.getenv("SUPABASE_IMAGES_BUCKET", "faceforge-images"),
        supabase_reports_bucket=os.getenv("SUPABASE_REPORTS_BUCKET", "faceforge-reports"),
        signed_url_ttl_seconds=int(os.getenv("SIGNED_URL_TTL_SECONDS", "3600")),
    )


settings = get_settings()
