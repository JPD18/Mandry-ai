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


LLM service prompt-
so the app uses llms to answer natural language questions thus we will need an llm_service.py file that makes sending posts to api modular similar to the following code, add this file 

# services/llm.py
import os
import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self,
                 base_url: str = None,
                 model_name: str = None,
                 timeout: int = 20):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
        self.model = model_name or os.getenv("OLLAMA_MODEL", "gemma3")
        self.timeout = timeout
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def call(
        self,
        system_prompt: str | None = None,
        user_message: str | None = None,
        extra_params: Dict[str, Any] | None = None,
    ) -> str:
        """High-level convenience wrapper for chat-completion endpoints.

        Typical usage (legacy):
            call("You are…", "Hello")

        Advanced usage (new):
            messages = [...]
            call(extra_params={"messages": messages})

        If *extra_params* contains a pre-built ``messages`` list, that list will
        be sent *verbatim* and *system_prompt* / *user_message* are ignored.
        """

        extra_params = extra_params or {}

        # If caller already built the full "messages" array, trust it.
        if "messages" in extra_params:
            payload = {
                "model": self.model,
                "stream": False,
            }
            # Avoid accidental duplication of model/stream keys from extra_params
            payload.update(extra_params)
        else:
            # Legacy 2-string interface
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or ""},
                    {"role": "user", "content": user_message or ""},
                ],
                "temperature": 0.9,
                "max_tokens": 100,
                "presence_penalty": 0.4,
                "frequency_penalty": 0.8,
                "stream": False,
            }
            # Additional OpenAI params (temperature, etc.)
            payload.update(extra_params)

        try:
            resp = requests.post(
                self.base_url, 
                json=payload, 
                headers=self.headers,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Handle Ollama API response format
            if "message" in data:
                # Direct message response
                return data["message"]["content"].strip()
            elif "choices" in data and len(data["choices"]) > 0:
                # OpenAI-compatible format
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise ValueError(f"Unexpected response format from Ollama API: {data}")
                
        except requests.exceptions.RequestException as e:
            logger.error(
                f"LLMService ➔ Request failed: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Payload:{payload}"
            )
            raise
        except (KeyError, ValueError) as e:
            logger.error(
                f"LLMService ➔ Invalid response format: {e}\n"
                f"  URL:    {self.base_url}\n"
                f"  MODEL:  {self.model}\n"
                f"  Payload:{payload}"
            )
            raise

# you can export a singleton for convenience
default_llm = LLMService()

RAG PROMPT-  create a rag based on this search, so extracting the main query from the users question, sending it to the valyu api, and feeding its response to the llm to enrich its context
## Implementing a static folder serving from djanogo:


Citations prompt- so in the chat page, when context is retrieved it is correctly fed to the LLM and then passed to the UI however the citations format and text formatting of the q&a does not work, investigate this and create a plan to make clear citations and text formatting

doc processing promtp - ok so for document upload it uploads docs but doesnt do anything, similar to valyu.py for search I want to make a modular section for doc upload and extraction so extracting the text from the doc for verification, the documents uploaded should not be stored anywhere only processed, the basic flow is upload doc, extract text, feed text to llm that verfies validity and returns true or false to it
this is the basic idea so keep it simple maintainable and modular for us to exntend it and change it easily in future

I have frontend files located in @/frontend folder which is build by npm run build and then I need to run next export. afterwards I need to move all of the static files to the new folder called static in @/backend, afterwards add code to backend for django server to serve static content there at the root of the api
Citations prompt- so in the chat page, when context is retrieved it is correctly fed to the LLM and then passed to the UI however the citations format and text formatting of the q&a does not work, investigate this and create a plan to make clear citations and text formatting

scheduling prompt- thanks for all your help so far claude youre great! lets enhance the schedule service in a similar way to the document service, it should be modular and maintainable following the best sotware practices. its main purpose is to remind the user about their visa appointments and visa expires, so should be a page that allows the user to add a deadline and the system sends a reminder to their email close to the time, review the current scheduler assess the requirements and determine the most efficient way to implement this feature of the app