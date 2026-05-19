# StudyFlow AI — AI Study Assistant

## Author
**Gimhani Dilmika**  
University of Jaffna  


---

## Project Overview

**StudyFlow AI** is a full-stack AI-powered study assistant chatbot built with **Python Flask** and the **Groq API**.  
The system provides a clean and modern chat interface where users can ask questions, learn programming concepts, get study explanations, generate interview preparation answers, and receive AI-based learning support.

This project focuses on building a practical AI web application with a Flask backend, API integration, responsive frontend design, and browser-based chat session management.

---

## Features

| Feature | Description |
|--------|-------------|
| 💬 **AI Chatbot** | Ask questions and receive AI-powered responses |
| 📚 **Study Assistant** | Get explanations for programming, learning topics, and study materials |
| 🧠 **Context Memory** | Maintains recent chat context during conversation |
| 🗂️ **Recent Chat Sessions** | Saves chat sessions in the browser using local storage |
| 🆕 **New Chat** | Start a new conversation anytime |
| 📋 **Copy Messages** | Copy assistant or user messages easily |
| ⬇️ **Download Chat** | Download the current chat as a `.txt` file |
| 🌙 **Dark / Light Mode** | Switch between dark and light themes |
| 🎨 **Modern UI** | Clean, responsive, user-friendly frontend |
| ⚡ **Groq API Integration** | Fast AI response generation using Groq model API |

---

## Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python Flask |
| AI API | Groq API |
| Environment Variables | python-dotenv |
| Server | Flask development server / Gunicorn for deployment |
| Storage | Browser LocalStorage for chat sessions |

---

## Project Structure

```text
ai-study-assistant/
├── app.py                  # Flask backend + frontend UI
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore              # Files ignored by Git
├── README.md               # Project documentation
├── database/
│   └── study.db            # Optional local database file
├── uploads/                # Optional upload folder
└── static/                 # Optional static assets