# FaceForge Backend

Production-ready FastAPI backend for the FaceForge forensic sketch console.

## Run locally

```powershell
cd C:\Users\Monisha\Desktop\FaceForge\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend integration

Set the React/Vite frontend API base URL to:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Call authenticated endpoints with:

```text
Authorization: Bearer <access_token>
```

## Important setup

Create these private Supabase storage buckets:

```text
faceforge-images
faceforge-reports
```

Run `supabase_schema.sql` in the Supabase SQL editor before using the API.

## Endpoints

```text
POST /auth/register
POST /auth/login
POST /sessions/create
GET  /sessions/{session_id}
POST /generate
POST /refine
POST /match
POST /export
GET  /audit
GET  /health
```
