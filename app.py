from flask import Flask, request, jsonify, render_template
import anthropic
import sqlite3
import uuid
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

DB_PATH = "database/study.db"
ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}

# ─── System Prompts ───────────────────────────────────────────────────────────

PROMPTS = {
    "summary": """You are an expert academic summarizer.
Given the following study material, create a clear and structured summary.
Format your response as:
## Overview
(2-3 sentence overview)

## Key Concepts
(bullet points of main concepts)

## Important Details
(bullet points of important facts/details)

## Key Takeaways
(3-5 bullet points the student must remember)

Be concise but comprehensive. Use simple language.""",

    "flashcards": """You are an expert educator creating flashcards.
Given the following study material, create 8-10 flashcards.
Return ONLY a valid JSON array like this:
[
  {"question": "What is...?", "answer": "..."},
  {"question": "Define...?", "answer": "..."}
]
Make questions clear and answers concise (1-3 sentences).
Cover the most important concepts. Return ONLY the JSON array, nothing else.""",

    "quiz": """You are an expert educator creating multiple choice quiz questions.
Given the following study material, create 5 multiple choice questions.
Return ONLY a valid JSON array like this:
[
  {
    "question": "What is...?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "explanation": "Brief explanation why this is correct"
  }
]
- correct is the index (0-3) of the correct option
- Make questions challenging but fair
- Cover different parts of the material
Return ONLY the JSON array, nothing else.""",

    "chat": """You are a helpful and patient AI study tutor.
The student is studying the provided material.
Answer their questions clearly and helpfully.
- Use examples when explaining concepts
- Break down complex ideas into simple steps
- Encourage the student
- If asked something not in the material, answer from your knowledge but mention it
Keep responses focused and educational.""",
}


# ─── Database ─────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs("database", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id TEXT PRIMARY KEY,
            doc_id TEXT,
            mode TEXT,
            result TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_document(filename, content):
    doc_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO documents VALUES (?, ?, ?, ?)",
        (doc_id, filename, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return doc_id


def get_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, filename, content, created_at FROM documents WHERE id=?", (doc_id,)
    ).fetchone()
    conn.close()
    if row:
        return {"id": row[0], "filename": row[1], "content": row[2], "created_at": row[3]}
    return None


def get_all_documents():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, filename, created_at FROM documents ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1], "created_at": r[2]} for r in rows]


def save_session(doc_id, mode, result):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO study_sessions VALUES (?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), doc_id, mode, result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def delete_document(doc_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.execute("DELETE FROM study_sessions WHERE doc_id=?", (doc_id,))
    conn.commit()
    conn.close()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath, filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext in ("txt", "md"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == "pdf":
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            return None
    return None


def call_ai(system, user_content, max_tokens=2000):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


# ─── Sessions (chat memory) ───────────────────────────────────────────────────
chat_sessions = {}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file. Use PDF, TXT, or MD"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    content = extract_text_from_file(filepath, filename)
    if not content or len(content.strip()) < 50:
        os.remove(filepath)
        return jsonify({"error": "Could not extract text. Make sure the file has readable content."}), 400

    content = content[:15000]  # Limit to 15k chars
    doc_id = save_document(filename, content)
    os.remove(filepath)  # Don't store file, just content

    return jsonify({
        "doc_id": doc_id,
        "filename": filename,
        "word_count": len(content.split()),
        "message": "File uploaded successfully!",
    })


@app.route("/api/paste", methods=["POST"])
def paste_text():
    data = request.get_json()
    text = data.get("text", "").strip()
    title = data.get("title", "Pasted Notes").strip()

    if len(text) < 50:
        return jsonify({"error": "Text too short. Please paste at least 50 characters."}), 400

    text = text[:15000]
    doc_id = save_document(title, text)

    return jsonify({
        "doc_id": doc_id,
        "filename": title,
        "word_count": len(text.split()),
        "message": "Notes saved successfully!",
    })


@app.route("/api/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    doc_id = data.get("doc_id")
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = call_ai(PROMPTS["summary"], f"Study material:\n\n{doc['content']}")
        save_session(doc_id, "summary", result)
        return jsonify({"summary": result, "timestamp": datetime.now().strftime("%H:%M")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/flashcards", methods=["POST"])
def flashcards():
    data = request.get_json()
    doc_id = data.get("doc_id")
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = call_ai(PROMPTS["flashcards"], f"Study material:\n\n{doc['content']}", max_tokens=1500)
        # Clean JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        cards = json.loads(result.strip())
        save_session(doc_id, "flashcards", json.dumps(cards))
        return jsonify({"flashcards": cards, "timestamp": datetime.now().strftime("%H:%M")})
    except Exception as e:
        return jsonify({"error": f"Failed to generate flashcards: {str(e)}"}), 500


@app.route("/api/quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    doc_id = data.get("doc_id")
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = call_ai(PROMPTS["quiz"], f"Study material:\n\n{doc['content']}", max_tokens=2000)
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        questions = json.loads(result.strip())
        save_session(doc_id, "quiz", json.dumps(questions))
        return jsonify({"questions": questions, "timestamp": datetime.now().strftime("%H:%M")})
    except Exception as e:
        return jsonify({"error": f"Failed to generate quiz: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    doc_id = data.get("doc_id")
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    if not message:
        return jsonify({"error": "Empty message"}), 400

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    history = chat_sessions[session_id]
    system = PROMPTS["chat"] + f"\n\nStudy material the student is working on:\n\n{doc['content'][:8000]}"

    history.append({"role": "user", "content": message})
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system,
            messages=history[-10:],
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        if len(history) > 20:
            chat_sessions[session_id] = history[-20:]
        return jsonify({
            "reply": reply,
            "session_id": session_id,
            "timestamp": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/documents", methods=["GET"])
def documents():
    return jsonify(get_all_documents())


@app.route("/api/documents/<doc_id>", methods=["DELETE"])
def delete_doc(doc_id):
    delete_document(doc_id)
    return jsonify({"success": True})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
