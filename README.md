## Author
Gimhani Dilmika — University of Jaffna
Decodelabs Internship Project 4

# AI Study Assistant — Project 4

A full-stack AI-powered study tool that turns any notes or PDF into summaries, flashcards, quizzes, and an AI tutor chat.

## Features

| Feature | Description |
|---------|-------------|
| 📋 **AI Summary** | Structured summary with key concepts, details, and takeaways |
| 🃏 **Flashcards** | 8-10 auto-generated click-to-flip flashcards |
| 📝 **Quiz** | 5 multiple choice questions with scoring and explanations |
| 💬 **AI Tutor Chat** | Ask anything about your material with memory |
| 📄 **PDF Upload** | Upload PDF, TXT, or MD files |
| 📋 **Paste Notes** | Paste text directly without a file |
| 🗂️ **Document Library** | Save and switch between multiple documents |

## Quick Start

```bash
# 1. Enter the project
cd ai-study-assistant

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run
python app.py
```

Visit **http://localhost:5000**

---

## Project Structure

```
ai-study-assistant/
├── app.py                  # Flask backend
├── requirements.txt
├── .env.example
├── database/
│   └── study.db            # Auto-created SQLite DB
├── uploads/                # Temp upload folder
├── templates/
│   └── index.html          # Main UI
└── static/
    ├── css/style.css
    └── js/app.js
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main UI |
| POST | `/api/upload` | Upload PDF/TXT file |
| POST | `/api/paste` | Save pasted text |
| POST | `/api/summarize` | Generate summary |
| POST | `/api/flashcards` | Generate flashcards |
| POST | `/api/quiz` | Generate quiz |
| POST | `/api/chat` | AI tutor chat |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/<id>` | Delete a document |

## Tech Stack

- Python 3.10+ / Flask 3.x
- Anthropic Claude API
- pdfplumber (PDF text extraction)
- SQLite (document storage)
- Vanilla JS — no framework needed
