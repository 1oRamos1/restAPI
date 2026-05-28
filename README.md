# Codyssey – Personalized Coding Learning Platform 🚀

**Codyssey** is a modern web platform that helps users learn programming by following curated and AI-generated learning tracks. Whether you're a beginner or an experienced coder, Codyssey provides structured challenges to sharpen your skills.

---

## 🌟 Features

- **Personalized Learning Tracks** – Choose a language, category, and difficulty level
- **AI-Powered Tasks** – Tasks are dynamically generated and graded by AI based on your performance
- **Premium Experience** – Pro users can generate custom learning tracks using OpenAI GPT-4
- **Progress Tracking** – Save solutions, track completion, and get AI-generated progress summaries
- **Multi-Language Support** – Python, JavaScript, C++ and more
- **Dark Mode** – Seamless light/dark theme switching
- **Google OAuth** – Sign in with Google

---

## 🖥 Live Demo

Try Codyssey online: [**Codyssey Live**](https://tracker-2528.onrender.com)

### Premium Access (Sandbox)

To explore Pro-only features:

- **Email:** `sb-ffrxc44858868@business.example.com`
- **Password:** `QiDzYd1-`

---

## 🛠 Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Tailwind CSS, React Router, Monaco Editor |
| Backend | Django REST Framework, dj-rest-auth, Django Allauth |
| AI | OpenAI GPT-4 (Pro users), Mistral (free users) |
| Database | PostgreSQL (production), SQLite (development) |
| Auth | Session-based, Google OAuth |
| Deployment | Render |
| DevOps | Docker, GitHub Actions CI |
| Docs | Swagger / OpenAPI |

---

## 🏗 Architecture

```
Frontend (React)
     ↓ REST API
Backend (Django REST Framework)
     ↓
Services Layer
  ├── ai_service.py     — OpenAI / Mistral integration
  ├── task_service.py   — Task generation & grading
  └── track_service.py  — Track creation & summaries
     ↓
PostgreSQL
```

---

## 🎯 How It Works

1. Browse categories and select a programming language
2. Follow curated learning tracks with practical coding tasks
3. Submit solutions — AI grades your code and gives feedback
4. Generate AI progress summaries after completing tasks
5. Pro users can create fully custom tracks by entering learning goals

---

## 🚀 Running Locally

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/1oRamos1/restAPI.git
cd restAPI
docker-compose up --build
```

Open: `http://localhost:8000`

### Option 2 — Manual setup

```bash
git clone https://github.com/1oRamos1/restAPI.git

# Backend
cd restAPI/mysite
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

Open: `http://localhost:3000`

---

## 📖 API Documentation

After running locally, visit:
```
http://localhost:8000/api/docs/
```

---

## ✅ Tests

```bash
cd mysite
python manage.py test tracker.tests
```

22 tests covering auth, learning tracks, task grading, AI generation, and summaries.

---

## 💼 Connect

[LinkedIn – Or Amos](https://www.linkedin.com/in/or-amos-377537306)
