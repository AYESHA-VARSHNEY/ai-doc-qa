# 🤖 AI Document & Multimedia Q&A

A full-stack AI-powered web application that allows users to upload PDF documents, audio, and video files and interact with an AI chatbot to ask questions, generate summaries, and extract timestamps from media content.

---

## 📸 Screenshots

### Register with your API Key
![Register](screenshots/01_register.png)

### Upload a PDF
![Upload](screenshots/03_pdf_upload.png)

### Chat with your Document
![Chat](screenshots/04_chat_question.png)

### Generate Summary
![Summary](screenshots/05_summary.png)

### Video Upload & Summary
![Video](screenshots/06_video_upload.png)

### API Documentation (Swagger)
![API Docs](screenshots/07_swagger_api.png)

### Docker Containers Running
![Docker](screenshots/08_docker.png)

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| AI / LLM | LiteLLM — supports Groq, Gemini, OpenAI, Anthropic |
| Vector Search | FAISS + LangChain |
| Transcription | Whisper API (Groq or OpenAI) |
| Database | MongoDB (Motor async driver) |
| Cache | Redis |
| Frontend | React 18 + Axios + React-Dropzone |
| Auth | JWT (python-jose) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 🔑 How API Keys Work

Each user provides their **own API key** at registration time.
The key is stored **only in browser localStorage** — never saved on the server or database.
This means anyone can clone and run this project using their own key — no shared secrets needed.

**Supported Providers:**

| Key Format | Provider | Cost |
|---|---|---|
| `gsk_...` | Groq | ✅ Free |
| `AIza...` | Google Gemini | ✅ Free |
| `sk-...` | OpenAI | Paid |
| `sk-ant-...` | Anthropic | Paid |

---

## 🚀 Setup & Running Instructions

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-doc-qa.git
cd ai-doc-qa
```

### Step 2 — Create .env file

**Mac/Linux:**
```bash
cp .env.example .env
```

**Windows PowerShell:**
```powershell
"JWT_SECRET=myapp2024secretxyz`nMONGO_URL=mongodb://mongo:27017" | Out-File -FilePath .env -Encoding utf8
```

Contents of `.env`:
```
JWT_SECRET=any_random_string_you_choose
MONGO_URL=mongodb://mongo:27017
```

> ⚠️ No API key needed in .env — each user provides their own at registration time.

### Step 3 — Run with Docker
```bash
docker compose up --build
```

- **Frontend** → http://localhost:3000
- **API Docs** → http://localhost:8000/docs

### Step 4 — Register & Use
1. Open http://localhost:3000
2. Click **Register**
3. Enter username, password, and your API key (Groq recommended — free at console.groq.com)
4. Login and start uploading files!

### Step 5 — Stop the app
```bash
docker compose down
```

To also delete stored data:
```bash
docker compose down -v
```

---

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ --cov=. --cov-report=term-missing -v
```

Expected output:
```
========================= test session starts ==========================
tests/test_all.py ..........................................    [100%]
---------- coverage: 96%+ ----------
PASSED
```

---

## 📡 API Documentation

Base URL: `http://localhost:8000`

All protected endpoints require two headers:
```
Authorization: Bearer <jwt_token>
X-OpenAI-Key: <your_api_key>
```

### Auth Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login and get JWT token |

**Register Request:**
```json
{
  "username": "ayesha",
  "password": "mypassword"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Upload Endpoint

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/upload/` | ✅ | Upload PDF / audio / video |

**Supported formats:** `.pdf`, `.mp3`, `.wav`, `.m4a`, `.mp4`, `.webm`

**Response:**
```json
{
  "file_id": "uuid-here",
  "file_name": "document.pdf",
  "file_type": "pdf",
  "message": "File uploaded and indexed successfully"
}
```

### Chat Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/chat/` | ✅ | Ask a question, get full answer |
| POST | `/chat/stream` | ✅ | Streaming response (SSE) |

**Request:**
```json
{
  "file_id": "uuid-here",
  "question": "What is this document about?"
}
```

**Response:**
```json
{
  "answer": "This document is about...",
  "timestamp": 12.5,
  "source": "document.pdf"
}
```

> `timestamp` is returned for audio/video files — indicates where in the media the answer was found.

### Summary Endpoint

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/summary/` | ✅ | Generate bullet-point summary |

**Request:**
```json
{
  "file_id": "uuid-here"
}
```

**Response:**
```json
{
  "summary": "• Point 1\n• Point 2\n• Point 3",
  "file_name": "document.pdf",
  "file_type": "pdf"
}
```

### Health Check

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | ❌ | Check if server is running |

---

## 📁 Project Structure

```
ai-doc-qa/
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── routers/
│   │   ├── auth.py                    # Register / Login / JWT
│   │   ├── upload.py                  # File upload + text extraction
│   │   ├── chat.py                    # Q&A + streaming responses
│   │   └── summary.py                 # AI summarization
│   ├── services/
│   │   ├── llm_service.py             # LiteLLM — supports any provider
│   │   ├── transcription_service.py   # Whisper transcription
│   │   └── vector_service.py          # MongoDB metadata storage
│   ├── models/
│   │   └── schemas.py                 # Pydantic request/response models
│   ├── tests/
│   │   └── test_all.py                # 95%+ coverage test suite
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main app component
│   │   ├── index.css                  # Global styles
│   │   └── components/
│   │       ├── Auth.jsx               # Login / Register with API key
│   │       ├── FileUpload.jsx         # Drag & drop uploader
│   │       ├── ChatBot.jsx            # Streaming chat UI
│   │       ├── Summary.jsx            # Summary display
│   │       └── MediaPlayer.jsx        # Timestamp + play button
│   ├── public/index.html
│   ├── package.json
│   └── Dockerfile
├── screenshots/                       # App screenshots
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions CI/CD pipeline
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## ✨ Features

- 📄 **PDF Q&A** — Upload any PDF and ask questions about it
- 🎵 **Audio Q&A** — Upload MP3/WAV, get transcription + ask questions
- 🎬 **Video Q&A** — Upload MP4, get transcription + timestamps
- 💬 **Real-time Streaming** — Responses stream token by token (SSE)
- 🔍 **Vector Search** — FAISS semantic search for accurate answers
- 📝 **Auto Summary** — One-click bullet-point summary
- 🔐 **JWT Auth** — Secure per-user authentication
- 🔑 **BYOK** — Bring Your Own Key (Groq, Gemini, OpenAI, Anthropic)
- 🐳 **Dockerized** — One command setup with Docker Compose
- ⚙️ **CI/CD** — Automated testing via GitHub Actions
