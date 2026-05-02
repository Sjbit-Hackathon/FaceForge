# FaceForge

A face-analysis and image-enhancement web application built with React + Vite (frontend) and FastAPI (backend).

---

## Getting Started

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd FaceForge_Backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create your local env file from the template:
cp .env.example .env
# Then open .env and fill in your real credentials (see below).

python -m app.main   # or: ./run_backend.bat on Windows
```

---

## Environment variables

Copy `FaceForge_Backend/.env.example` to `FaceForge_Backend/.env` and replace every placeholder with a real value.

| Variable | Where to get it |
|---|---|
| `JWT_SECRET` | Generate locally: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `HUGGINGFACE_API_TOKEN` | [Hugging Face settings → Tokens](https://huggingface.co/settings/tokens) |
| `SUPABASE_URL` | Supabase project → Settings → API |
| `SUPABASE_ANON_KEY` | Supabase project → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase project → Settings → API (**keep secret — never commit**) |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase project → Settings → API |

> **Never commit `.env` or any file containing real credentials to the repository.**
> The `.gitignore` already excludes `.env` and `.env.*` (while keeping `.env.example`).

---

## Rotating credentials

If you believe credentials have been exposed:

1. **Supabase keys** — Go to _Project Settings → API_ and click **Regenerate** next to each key.
2. **Gemini API key** — Revoke the key in [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new one.
3. **Hugging Face token** — Delete the token in [account settings](https://huggingface.co/settings/tokens) and generate a new one.
4. **JWT secret** — Generate a new random value and restart the backend.

After rotating, update your `.env` file and redeploy.

To permanently remove a secret from git history, use [`git filter-repo`](https://github.com/newren/git-filter-repo) or [BFG Repo Cleaner](https://rtyley.github.io/bfg-repo-cleaner/), then force-push and notify all collaborators to re-clone.

---

## Secret scanning

We recommend running [gitleaks](https://github.com/gitleaks/gitleaks) before every push:

```bash
# Install (once)
brew install gitleaks   # or: https://github.com/gitleaks/gitleaks/releases

# Scan the repository
gitleaks detect --source . --verbose
```

A `.gitleaks.toml` configuration file can be added to the repo root to customise rules.

---

## React + Vite

This project uses [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) (Oxc transform) for fast refresh and ESLint rules.
See the [Vite docs](https://vite.dev) for full configuration reference.
