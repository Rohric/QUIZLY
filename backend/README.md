# Quizzly API

A REST API backend for an AI-powered quiz generation application, built with Django and Django REST Framework. It uses YouTube videos as input, transcribes them with Whisper, and generates quizzes via the Gemini API.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Required Libraries](#required-libraries)
- [Running the Server](#running-the-server)
- [Authentication & User Workflow](#authentication--user-workflow)
- [API Reference](#api-reference)
- [Data Models](#data-models)

---

## Project Structure

```
backend/
├── core/                   # Project settings, root URLs
├── user_auth_app/          # Registration, login, user profiles
│   └── api/                # Serializers, views, URLs
├── quizzes_app/            # Quiz creation and management
│   ├── api/                # Serializers, views, URLs
│   └── services/           # yt-dlp, Whisper, Gemini logic
├── .env                    # Secret keys & local config (never commit this)
├── .env.template           # Template with placeholder values
└── manage.py
```

---

## Setup & Installation

**1. Clone the repository**

```bash
git clone https://github.com/Rohric/QUIZLY
cd backend
```

**2. Create and activate a virtual environment**

```bash
python -m venv env

# Windows
env\Scripts\activate

# macOS / Linux
source env/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up your environment file** — see the section below.

**5. Apply migrations**

```bash
python manage.py migrate
```

**6. (Optional) Create a superuser for the Django admin**

```bash
python manage.py createsuperuser
```

---

## Environment Variables

This project uses a `.env` file to keep secrets out of version control. The file is listed in `.gitignore` and must **never** be committed.

**Step 1 — Copy the template**

```bash
cp .env.template .env
```

**Step 2 — Fill in your `.env` file**

```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your-gemini-api-key
```

You can generate a Django secret key with:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Your Gemini API key can be obtained for free at https://ai.google.dev/.

---

## Required Libraries

### FFmpeg

Required by yt-dlp and Whisper for audio processing.

**Windows**
```powershell
winget install --id Gyan.FFmpeg.Essentials -e --source winget
```

Then add the `bin` folder to your system PATH environment variable.

**macOS**
```bash
brew install ffmpeg
```

### Python Libraries

All Python dependencies are listed in `requirements.txt`. Key libraries:

| Library | Purpose |
|---------|---------|
| `yt-dlp` | Download audio from YouTube |
| `openai-whisper` | Transcribe audio to text |
| `google-genai` | Generate quiz questions via Gemini API |

---

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Authentication & User Workflow

This API uses **JWT Cookie-based authentication**. After login, `access_token` and `refresh_token` are set as `httpOnly` cookies automatically. Every protected endpoint reads the token from these cookies.

### Full Workflow: From Registration to Creating a Quiz

---

#### 1. Register a new account

**`POST /api/register/`** — No authentication required.

```json
// Request body
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

```json
// Response 201
{
  "detail": "User created successfully!"
}
```

---

#### 2. Log in

**`POST /api/login/`** — No authentication required.

```json
// Request body
{
  "username": "your_username",
  "password": "your_password"
}
```

```json
// Response 200
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

`access_token` and `refresh_token` cookies are set automatically.

---

#### 3. Create a quiz from a YouTube video

**`POST /api/quizzes/`** — Requires authentication.

The API downloads the audio, transcribes it with Whisper, and generates 10 questions via Gemini. This may take a few minutes depending on video length.

```json
// Request body
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

```json
// Response 201
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "created_at": "2023-07-29T12:34:56.789Z",
      "updated_at": "2023-07-29T12:34:56.789Z"
    }
  ]
}
```

---

#### 4. Refresh your access token

**`POST /api/token/refresh/`** — Requires valid `refresh_token` cookie.

The `access_token` expires after a short period. Use this endpoint to get a new one without logging in again.

```json
// Response 200
{
  "detail": "Token refreshed"
}
```

---

#### 5. Log out

**`POST /api/logout/`** — Requires authentication.

Deletes both cookies. The tokens are no longer valid after this.

---

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/register/` | ❌ | Register a new user |
| POST | `/api/login/` | ❌ | Log in, sets auth cookies |
| POST | `/api/logout/` | ✅ | Log out, deletes auth cookies |
| POST | `/api/token/refresh/` | Cookie | Refresh the access token |
| GET | `/api/auth/profile/` | ✅ | Get own profile |
| PATCH | `/api/auth/profile/` | ✅ | Update own profile |

### Quizzes

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/quizzes/` | ✅ | Create a new quiz from a YouTube URL |
| GET | `/api/quizzes/` | ✅ | List all own quizzes |
| GET | `/api/quizzes/{id}/` | ✅ | Get a single quiz |
| PATCH | `/api/quizzes/{id}/` | ✅ Owner only | Update quiz title or description |
| DELETE | `/api/quizzes/{id}/` | ✅ Owner only | Delete a quiz permanently |

---

## Data Models

### Quiz

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `title` | string | Quiz title generated by Gemini |
| `description` | string | Short summary generated by Gemini |
| `video_url` | string | The YouTube URL the quiz was created from |
| `status` | string | `processing`, `completed`, `failed` |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Question

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `question_title` | string | The question text |
| `question_options` | array | List of 4 answer options |
| `answer` | string | The correct answer from `question_options` |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### Quiz Status Values

| Status | Description |
|--------|-------------|
| `processing` | Audio is being downloaded and transcribed |
| `completed` | Quiz was successfully generated |
| `failed` | An error occurred during processing |
