from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import audit, auth, export, generate, match, refine, sessions
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="FaceForge forensic sketch backend for AI generation, refinement, storage, audit, and reports.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(sessions.router, prefix=settings.api_prefix)
app.include_router(generate.router, prefix=settings.api_prefix)
app.include_router(refine.router, prefix=settings.api_prefix)
app.include_router(match.router, prefix=settings.api_prefix)
app.include_router(export.router, prefix=settings.api_prefix)
app.include_router(audit.router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "service": "FaceForge", "environment": settings.environment}
