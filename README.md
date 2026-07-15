# Quizly – Backend

> Turn YouTube videos into quizzes | REST API built with Django & Django REST Framework

With Quizly you can effortlessly turn YouTube videos into exciting quizzes! Using
AI technology, the app analyzes a video's content and automatically generates an
interactive quiz with 10 questions. Perfect for learning, revising, or just having
fun. Give it a try and test your knowledge in a new, entertaining way!

This repository contains **the backend only**, which provides all data and
business logic through a REST API. The corresponding frontend communicates with
this backend via these endpoints.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation & Configuration](#installation--configuration)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Frontend](#frontend)
- [Author](#author)

---

## Prerequisites

- Python 3.14.5+
- pip 26.1.1+
- FFmpeg, installed system-wide (required by `yt-dlp` and Whisper)
- A Google Gemini API key, obtainable for free at https://ai.google.dev/

### Installing FFmpeg

**Windows – via terminal**

```bash
winget install --id Gyan.FFmpeg -e --source winget
```

**macOS**

```bash
# Install Homebrew, if not already installed:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg:
brew install ffmpeg
```

**Linux**

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install ffmpeg
```

---

## Installation & Configuration

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd Quizly_Backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Mac/Linux
   .venv\Scripts\activate           # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file – sensitive settings are not stored directly in
   `core/settings.py` but loaded from a local `.env` file (ignored by Git):

   ```bash
   cp .env.template .env
   ```

5. Generate a new `SECRET_KEY` and add it to the `.env` file:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Add the generated key and the following values to your `.env` file:

   ```env
   SECRET_KEY='your_generated_key_here'
   DEBUG=True
   ALLOWED_HOSTS=["your-api-domain.com","127.0.0.1","localhost"]
   CORS_ALLOWED_ORIGINS=["https://your-frontend-domain.com","http://127.0.0.1:5500"]
   GEMINI_API_KEY='your_gemini_api_key_here'
   ```

   > **Note:** Use `DEBUG=True` for local development only. Set it to `False` in
   > production and update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` to match
   > your actual domain(s).

   > **Gemini API key:** Required for AI-based quiz generation. Get a free key
   > at https://ai.google.dev/ and add it to your `.env` file as
   > `GEMINI_API_KEY`.

6. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

   The API will be available at: `http://127.0.0.1:8000/`

---

## Project Structure

```
01_DEV/
├── core/               # Django project configuration (settings, urls, wsgi)
├── accounts/           # User authentication (register, login, logout, token refresh)
│   └── api/            # Serializers, views, URLs for authentication
├── quiz_management/    # Quiz creation, management and retrieval
│   └── api/            # Serializers, views, URLs for quizzes
├── manage.py
└── requirements.txt
```

---

## API Endpoints

> For full endpoint documentation including request/response examples, status
> codes and permissions, see [docs/api.md](docs/api.md).

### Authentication

Login and registration

| Method | Endpoint              | Description          | Auth required | Access         |
| ------ | --------------------- | -------------------- | ------------- | -------------- |
| POST   | `/api/register/`      | Register a new user  | No            | All            |
| POST   | `/api/login/`         | Log in a user        | No            | All            |
| POST   | `/api/logout/`        | Log out a user       | Yes           | Logged-in user |
| POST   | `/api/token/refresh/` | Refresh access token | Yes           | Logged-in user |

### Quiz Management

Creation, management and retrieval of quizzes

| Method | Endpoint             | Description       | Auth required | Access         |
| ------ | -------------------- | ----------------- | ------------- | -------------- |
| POST   | `/api/quizzes/`      | Create a new quiz | Yes           | Logged-in user |
| GET    | `/api/quizzes/`      | List all quizzes  | Yes           | Logged-in user |
| GET    | `/api/quizzes/{id}/` | Retrieve one quiz | Yes           | Logged-in user |
| PATCH  | `/api/quizzes/{id}/` | Update one quiz   | Yes           | Quiz owner     |
| DELETE | `/api/quizzes/{id}/` | Delete one quiz   | Yes           | Quiz owner     |

---

## Frontend

The corresponding frontend repository can be found here:

[Frontend Repository](https://github.com/PBiebert/Quizly_Frontend)

---

## Author

**Philipp Biebert**
Project status: 07.07.2026
