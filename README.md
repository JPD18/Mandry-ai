# Mandry AI - Visa & Immigration Assistant

A hackathon MVP for an AI-powered visa and immigration consultant assistant. This is a basic RAG application that allows users to upload visa documents, ask questions, and schedule appointments.

## Project Structure

```
Mandry-ai/
├── backend/          # Django REST API
├── frontend/         # Next.js 14 frontend
├── docs/            # Documentation
├── env.template     # Environment variables template
└── README.md
```

## Quick Start

### Backend Setup (Django)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the template to backend directory
   cp ../env.template .env
   # Edit .env with your API keys
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Django server:**
   ```bash
   python manage.py runserver 8000
   ```

### Frontend Setup (Next.js)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   # Create .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

## Usage

1. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

2. **Features:**
   - **Chat Interface (/)**: Ask questions about visa and immigration
   - **Document Upload (/upload)**: Upload PDF, PNG, or JPG documents
   - **Appointments (/reminders)**: Schedule consultations and appointments

## API Endpoints

- `POST /api/upload/` - Upload documents (PDF/PNG/JPG)
- `POST /api/ask/` - Ask questions and get AI responses
- `POST /api/schedule/` - Schedule appointments

## Environment Variables

Copy `env.template` and configure:

```env
# Backend
OPENAI_API_KEY=your_openai_api_key_here
VALYU_KEY=your_valyu_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Technology Stack

**Backend:**
- Django 4.2
- Django REST Framework
- SQLite database
- CORS headers for frontend integration

**Frontend:**
- Next.js 14 with TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide React icons

## Development Notes

- This is an MVP for hackathon purposes - minimal styling and testing
- File uploads are saved to `backend/media/` directory
- Stub responses are provided for AI functionality
- Appointment reminders are logged to console
- No authentication/authorization implemented
- SQLite database for simplicity

## Production Considerations

For production deployment, consider:
- Replace SQLite with PostgreSQL/MySQL
- Implement proper authentication
- Add file storage (AWS S3, etc.)
- Integrate real AI/LLM services
- Add proper error handling and logging
- Implement proper security measures
- Add tests and CI/CD pipeline