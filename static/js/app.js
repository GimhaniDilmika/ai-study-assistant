'use strict';

let currentDocId = null;
let currentMode = 'summary';
let sessionId = null;
let quizAnswers = {};
let quizData = [];

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  loadDocuments();
  setupDragDrop();
});

// ── Drag & Drop ───────────────────────────────────────────────────────────────
function setupDragDrop() {
  const zone = document.getElementById('drop-zone');
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
}

// ── Upload ────────────────────────────────────────────────────────────────────
function uploadFile(input) {
  const file = input.files[0];
  if (file) handleFile(file);
}

async function handleFile(file) {
  const zone = document.getElementById('drop-zone');
  zone.innerHTML = '<div class="spinner"></div><span>Uploading...</span>';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      resetDropZone();
      return;
    }
    await loadDocuments();
    selectDocument(data.doc_id, data.filename, data.word_count);
    resetDropZone();
  } catch {
    alert('Upload failed. Please try again.');
    resetDropZone();
  }
}

function resetDropZone() {
  document.getElementById('drop-zone').innerHTML = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
    <span>Drop PDF or TXT here</span>
    <small>or click to browse</small>`;
  document.getElementById('file-input').value = '';
}

// ── Paste ─────────────────────────────────────────────────────────────────────
function showPasteModal() { document.getElementById('paste-modal').style.display = 'flex'; }
function hidePasteModal() { document.getElementById('paste-modal').style.display = 'none'; }

async function pasteText() {
  const text = document.getElementById('paste-text').value.trim();
  const title = document.getElementById('paste-title').value.trim() || 'Pasted Notes';
  if (text.length < 50) { alert('Please paste at least 50 characters.'); return; }

  try {
    const res = await fetch('/api/paste', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    hidePasteModal();
    document.getElementById('paste-text').value = '';
    document.getElementById('paste-title').value = '';
    await loadDocuments();
    selectDocument(data.doc_id, data.filename, data.word_count);
  } catch { alert('Failed to save notes.'); }
}

// ── Documents ─────────────────────────────────────────────────────────────────
async function loadDocuments() {
  const res = await fetch('/api/documents');
  const docs = await res.json();
  const list = document.getElementById('docs-list');
  if (!docs.length) {
    list.innerHTML = '<div class="empty-docs">No documents yet</div>';
    return;
  }
  list.innerHTML = docs.map(d => `
    <div class="doc-item ${d.id === currentDocId ? 'active' : ''}" id="doc-item-${d.id}" onclick="selectDocument('${d.id}', '${escHtml(d.filename)}')">
      <span class="doc-item-name">📄 ${escHtml(d.filename)}</span>
      <button class="doc-delete" onclick="event.stopPropagation();deleteDoc('${d.id}')" title="Delete">✕</button>
    </div>
  `).join('');
}

function selectDocument(docId, filename, wordCount) {
  currentDocId = docId;
  sessionId = null;
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('study-area').style.display = 'flex';
  document.getElementById('study-area').style.flexDirection = 'column';
  document.getElementById('study-area').style.flex = '1';
  document.getElementById('study-area').style.overflow = 'hidden';
  document.getElementById('doc-name').textContent = filename;
  document.getElementById('doc-words').textContent = wordCount ? `· ${wordCount} words` : '';
  clearOutputs();
  switchMode('summary');
  document.querySelectorAll('.doc-item').forEach(el => el.classList.remove('active'));
  const item = document.getElementById(`doc-item-${docId}`);
  if (item) item.classList.add('active');
}

async function deleteDoc(docId) {
  if (!confirm('Delete this document?')) return;
  await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
  if (currentDocId === docId) {
    currentDocId = null;
    document.getElementById('welcome-screen').style.display = 'flex';
    document.getElementById('study-area').style.display = 'none';
  }
  loadDocuments();
}

function clearOutputs() {
  document.getElementById('summary-output').style.display = 'none';
  document.getElementById('summary-output').innerHTML = '';
  document.getElementById('flashcards-output').innerHTML = '';
  document.getElementById('quiz-output').innerHTML = '';
  document.getElementById('quiz-result').style.display = 'none';
  document.getElementById('chat-messages').innerHTML = '';
  quizAnswers = {};
  quizData = [];
}

// ── Mode switching ────────────────────────────────────────────────────────────
function switchMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-tab').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
  document.querySelectorAll('.mode-content').forEach(c => c.classList.remove('active'));
  document.getElementById(`mode-${mode}`).classList.add('active');
}

// ── Summary ───────────────────────────────────────────────────────────────────
async function generateSummary() {
  if (!currentDocId) return;
  document.getElementById('summary-output').style.display = 'none';
  document.getElementById('summary-loading').style.display = 'flex';

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: currentDocId }),
    });
    const data = await res.json();
    document.getElementById('summary-loading').style.display = 'none';
    if (data.error) { alert(data.error); return; }

    const out = document.getElementById('summary-output');
    out.innerHTML = formatMarkdown(data.summary);
    out.style.display = 'block';
  } catch { document.getElementById('summary-loading').style.display = 'none'; alert('Failed to generate summary.'); }
}

// ── Flashcards ────────────────────────────────────────────────────────────────
async function generateFlashcards() {
  if (!currentDocId) return;
  document.getElementById('flashcards-output').innerHTML = '';
  document.getElementById('flashcards-loading').style.display = 'flex';

  try {
    const res = await fetch('/api/flashcards', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: currentDocId }),
    });
    const data = await res.json();
    document.getElementById('flashcards-loading').style.display = 'none';
    if (data.error) { alert(data.error); return; }

    const grid = document.getElementById('flashcards-output');
    grid.innerHTML = data.flashcards.map((card, i) => `
      <div class="flashcard" onclick="this.classList.toggle('flipped')">
        <div class="card-num">Card ${i + 1} of ${data.flashcards.length} · Click to flip</div>
        <div class="front">${escHtml(card.question)}</div>
        <div class="back">${escHtml(card.answer)}</div>
      </div>
    `).join('');
  } catch { document.getElementById('flashcards-loading').style.display = 'none'; alert('Failed to generate flashcards.'); }
}

// ── Quiz ──────────────────────────────────────────────────────────────────────
async function generateQuiz() {
  if (!currentDocId) return;
  document.getElementById('quiz-output').innerHTML = '';
  document.getElementById('quiz-result').style.display = 'none';
  document.getElementById('quiz-loading').style.display = 'flex';
  quizAnswers = {};

  try {
    const res = await fetch('/api/quiz', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: currentDocId }),
    });
    const data = await res.json();
    document.getElementById('quiz-loading').style.display = 'none';
    if (data.error) { alert(data.error); return; }

    quizData = data.questions;
    const container = document.getElementById('quiz-output');
    container.innerHTML = data.questions.map((q, qi) => `
      <div class="quiz-q" id="quiz-q-${qi}">
        <div class="quiz-q-num">Question ${qi + 1}</div>
        <div class="quiz-q-text">${escHtml(q.question)}</div>
        <div class="quiz-options">
          ${q.options.map((opt, oi) => `
            <button class="quiz-option" onclick="selectOption(${qi}, ${oi})" id="opt-${qi}-${oi}">${escHtml(opt)}</button>
          `).join('')}
        </div>
        <div class="quiz-explanation" id="exp-${qi}">${escHtml(q.explanation)}</div>
      </div>
    `).join('') + `<button class="quiz-submit" onclick="submitQuiz()">Submit Quiz</button>`;
  } catch { document.getElementById('quiz-loading').style.display = 'none'; alert('Failed to generate quiz.'); }
}

function selectOption(qi, oi) {
  document.querySelectorAll(`#quiz-q-${qi} .quiz-option`).forEach(b => b.classList.remove('selected'));
  document.getElementById(`opt-${qi}-${oi}`).classList.add('selected');
  quizAnswers[qi] = oi;
}

function submitQuiz() {
  if (Object.keys(quizAnswers).length < quizData.length) {
    alert('Please answer all questions before submitting.'); return;
  }
  let correct = 0;
  quizData.forEach((q, qi) => {
    const chosen = quizAnswers[qi];
    document.querySelectorAll(`#quiz-q-${qi} .quiz-option`).forEach(b => b.disabled = true);
    document.getElementById(`opt-${qi}-q.correct`);
    if (chosen === q.correct) {
      correct++;
      document.getElementById(`opt-${qi}-${chosen}`).classList.add('correct');
    } else {
      document.getElementById(`opt-${qi}-${chosen}`).classList.add('wrong');
      document.getElementById(`opt-${qi}-${q.correct}`).classList.add('correct');
    }
    document.getElementById(`exp-${qi}`).style.display = 'block';
  });
  const result = document.getElementById('quiz-result');
  const pct = Math.round((correct / quizData.length) * 100);
  result.innerHTML = `
    <div class="quiz-score">${correct}/${quizData.length}</div>
    <div class="quiz-score-label">${pct}% — ${pct >= 80 ? '🎉 Excellent!' : pct >= 60 ? '👍 Good job!' : '📚 Keep studying!'}</div>
  `;
  result.style.display = 'block';
  result.scrollIntoView({ behavior: 'smooth' });
}

// ── Chat ──────────────────────────────────────────────────────────────────────
async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg || !currentDocId) return;
  input.value = '';

  appendChatMsg(msg, 'user');
  document.getElementById('chat-typing').style.display = 'flex';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ doc_id: currentDocId, message: msg, session_id: sessionId }),
    });
    const data = await res.json();
    document.getElementById('chat-typing').style.display = 'none';
    if (data.error) { appendChatMsg('Sorry, something went wrong. Please try again.', 'bot'); return; }
    sessionId = data.session_id;
    appendChatMsg(data.reply, 'bot');
  } catch {
    document.getElementById('chat-typing').style.display = 'none';
    appendChatMsg('Connection error. Is the server running?', 'bot');
  }
}

function askQuick(text) {
  document.getElementById('chat-input').value = text;
  sendChat();
}

function appendChatMsg(text, role) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `chat-msg ${role}`;
  div.innerHTML = `${escHtml(text)}<div class="chat-msg-time">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatMarkdown(text) {
  return text
    .replace(/## (.+)/g, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n\n/g, '<br/>');
}
