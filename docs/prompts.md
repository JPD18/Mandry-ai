# Prompts

## Original Scaffold Request

# Goal
Scaffold **"Mandry-ai"** with a Django back-end and a Next.js front-end, all localhost-only. mandry is a visa and immigration consultant ai agent assistant that is a basic rag app that allows you to upload vida docs, ask questions and check requirements against official information, also scheduling appointments and sending reminders, this is for a hackathon so only needs to be a working mvp 

## Deliverables (single code dump)
1. **Monorepo**:
   - `/frontend` → Next.js 14, TS, Tailwind, shadcn/ui.
   - `/backend`  → Django , Django REST Framework, LangChain-py.
2. `.env.template` listing OPENAI_KEY, VALYU_KEY, TWILIO_*, etc.
3. **Backend** (`mandry_ai` project):
   - `visa` app with three DRF views:
     * `POST /api/upload`   – accept PDF/PNG/JPG, save to `media/`, return `{file_id}`.
     * `POST /api/ask`      – body `{question}`; return `{answer:"stub", citations:[]}`.
     * `POST /api/schedule` – body `{user, type, iso_date}`; log "Reminder scheduled".
   - `settings.py` uses SQLite, `django-cors-headers`, `rest_framework`.
4. **Frontend** pages:
   - `/` chat UI calling `/api/ask`.
   - `/upload` drag-and-drop uploader.
   - `/reminders` simple form.

6. **Prompt log**
   - `docs/prompts.md` contains THIS prompt at top.

## Constraints
- No Docker or cloud deploy — run with:
    * `python manage.py runserver 8000`
    * `npm run dev`
- Keep code minimal; no tests or styling polish.
- Reply **only** with code blocks, each preceded by `### <filepath>`. 