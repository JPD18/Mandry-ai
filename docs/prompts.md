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

## Authentication Implementation (Added)
prompt - add a basic user log in and sign up page to the front end and backend, it only needs username, email, password for now
### Backend Authentication
- Added Django REST Framework token authentication
- New API endpoints:
  * `POST /api/signup` - Create user account (username, email, password)
  * `POST /api/login` - Authenticate user and return token
- Updated `settings.py`:
  * Added `rest_framework.authtoken` to `INSTALLED_APPS`
  * Added `TokenAuthentication` to `DEFAULT_AUTHENTICATION_CLASSES`
- Token-based authentication using Django's built-in User model

### Frontend Authentication
- New pages:
  * `/login` - User login form
  * `/signup` - User registration form
- Features:
  * Form validation (password confirmation, minimum length)
  * Error handling with user feedback
  * Token storage in localStorage
  * Automatic redirect after successful authentication
- Updated navigation to include Login/Sign Up links
- Used shadcn/ui components for consistent styling

### Usage
1. Users are redirected to login/signup pages when not authenticated
2. Users can create accounts with username, email, and password
3. Login returns authentication token for API requests
4. Frontend stores token and user info in localStorage
5. All forms include proper validation and error handling
6. Protected routes (/, /upload, /reminders) require authentication
7. Navigation shows different options based on authentication status

### Database
- Run `python manage.py migrate` to create authentication tables
- Django's built-in User model stores user credentials
- Tokens stored in `authtoken_token` table 