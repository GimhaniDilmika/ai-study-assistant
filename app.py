from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template_string
import os
import json
import urllib.request
import urllib.error

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>StudyFlow AI</title>

  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    :root {
      --bg: #f5f7fb;
      --panel: #ffffff;
      --panel-soft: #f8fafc;
      --border: #e5e7eb;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --user-bubble: #2563eb;
      --bot-bubble: #ffffff;
      --danger: #ef4444;
      --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      --radius-xl: 26px;
      --radius-lg: 20px;
      --radius-md: 16px;
    }

    body.dark {
      --bg: #0b1220;
      --panel: #111827;
      --panel-soft: #0f172a;
      --border: #1f2937;
      --text: #f8fafc;
      --muted: #94a3b8;
      --primary: #3b82f6;
      --primary-dark: #2563eb;
      --user-bubble: #2563eb;
      --bot-bubble: #0f172a;
      --danger: #ef4444;
      --shadow: 0 12px 30px rgba(0, 0, 0, 0.28);
    }

    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      overflow: hidden;
    }

    .app {
      display: grid;
      grid-template-columns: 280px 1fr;
      height: 100vh;
    }

    .sidebar {
      background: var(--panel);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 18px;
      gap: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 6px 4px;
    }

    .brand-logo {
      width: 42px;
      height: 42px;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--primary), #60a5fa);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
      font-size: 18px;
      box-shadow: var(--shadow);
    }

    .brand h1 {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.03em;
    }

    .brand p {
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
    }

    .new-chat-btn {
      width: 100%;
      border: none;
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: white;
      padding: 14px 16px;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      transition: 0.2s;
      box-shadow: var(--shadow);
    }

    .new-chat-btn:hover {
      transform: translateY(-1px);
      opacity: 0.96;
    }

    .sidebar-label {
      font-size: 12px;
      font-weight: 800;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-top: 2px;
    }

    .session-list {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding-right: 4px;
    }

    .session-list::-webkit-scrollbar {
      width: 6px;
    }

    .session-list::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 999px;
    }

    body.dark .session-list::-webkit-scrollbar-thumb {
      background: #334155;
    }

    .session-item {
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
      border-radius: 14px;
      padding: 12px 14px;
      text-align: left;
      cursor: pointer;
      transition: 0.2s;
      font: inherit;
    }

    .session-item:hover,
    .session-item.active {
      border-color: #bfdbfe;
      background: #eff6ff;
    }

    body.dark .session-item:hover,
    body.dark .session-item.active {
      background: #172033;
      border-color: #2b4266;
    }

    .session-item-title {
      font-size: 14px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .session-item-meta {
      font-size: 12px;
      color: var(--muted);
      margin-top: 4px;
    }

    .sidebar-actions {
      display: grid;
      gap: 10px;
      border-top: 1px solid var(--border);
      padding-top: 16px;
    }

    .side-action {
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
      border-radius: 14px;
      padding: 12px 14px;
      font: inherit;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      transition: 0.2s;
    }

    .side-action:hover {
      background: #eff6ff;
    }

    body.dark .side-action:hover {
      background: #172033;
    }

    .main {
      display: flex;
      flex-direction: column;
      min-width: 0;
      height: 100vh;
    }

    .topbar {
      height: 74px;
      background: var(--panel);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
    }

    .topbar-left h2 {
      font-size: 18px;
      font-weight: 800;
      letter-spacing: -0.02em;
    }

    .topbar-left p {
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .pill {
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--muted);
      padding: 10px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
    }

    .icon-btn {
      width: 42px;
      height: 42px;
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
      border-radius: 12px;
      cursor: pointer;
      font-size: 16px;
      transition: 0.2s;
    }

    .icon-btn:hover {
      background: #eff6ff;
    }

    body.dark .icon-btn:hover {
      background: #172033;
    }

    .content {
      flex: 1;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .welcome {
      max-width: 900px;
      margin: 0 auto;
      width: 100%;
      padding: 54px 28px 24px;
      text-align: center;
    }

    .welcome h3 {
      font-size: clamp(36px, 6vw, 58px);
      line-height: 1.05;
      letter-spacing: -0.05em;
      font-weight: 800;
    }

    .welcome h3 span {
      color: var(--primary);
    }

    .welcome p {
      margin-top: 14px;
      font-size: 16px;
      color: var(--muted);
      max-width: 700px;
      margin-left: auto;
      margin-right: auto;
      line-height: 1.7;
    }

    .suggestions {
      margin-top: 34px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      text-align: left;
    }

    .suggestion-card {
      border: 1px solid var(--border);
      background: var(--panel);
      border-radius: 20px;
      padding: 20px;
      cursor: pointer;
      transition: 0.2s;
      box-shadow: var(--shadow);
      min-height: 118px;
    }

    .suggestion-card:hover {
      transform: translateY(-2px);
      border-color: #bfdbfe;
    }

    .suggestion-card b {
      display: block;
      font-size: 15px;
      line-height: 1.5;
      margin-bottom: 14px;
    }

    .suggestion-card span {
      font-size: 13px;
      color: var(--muted);
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 10px 22px 170px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      max-width: 980px;
      width: 100%;
      margin: 0 auto;
    }

    .messages::-webkit-scrollbar {
      width: 8px;
    }

    .messages::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 999px;
    }

    body.dark .messages::-webkit-scrollbar-thumb {
      background: #334155;
    }

    .row {
      display: flex;
      gap: 12px;
      align-items: flex-start;
      animation: fadeUp 0.2s ease;
    }

    .row.user {
      justify-content: flex-end;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      color: white;
      font-size: 16px;
      flex: 0 0 auto;
    }

    .avatar.bot {
      background: linear-gradient(135deg, var(--primary), #60a5fa);
    }

    .avatar.user {
      background: linear-gradient(135deg, #f97316, #fb7185);
    }

    .bubble-wrap {
      max-width: 72%;
    }

    .row.user .bubble-wrap {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }

    .bubble-head {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 11px;
      color: var(--muted);
      font-weight: 800;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .row.user .bubble-head {
      justify-content: flex-end;
    }

    .copy-btn {
      border: none;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
      font-size: 11px;
      font-weight: 800;
    }

    .copy-btn:hover {
      color: var(--primary);
    }

    .bubble {
      background: var(--bot-bubble);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 16px 18px;
      font-size: 15px;
      line-height: 1.75;
      box-shadow: var(--shadow);
      white-space: pre-wrap;
      word-break: break-word;
    }

    .row.user .bubble {
      background: var(--user-bubble);
      color: white;
      border-color: transparent;
    }

    .bubble pre {
      background: #0f172a;
      color: #f8fafc;
      padding: 14px;
      border-radius: 14px;
      overflow-x: auto;
      margin: 12px 0;
      font-size: 13px;
    }

    .bubble code {
      background: rgba(37, 99, 235, 0.12);
      padding: 2px 6px;
      border-radius: 7px;
    }

    .composer-wrap {
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      padding: 18px 22px 22px;
      background: linear-gradient(to top, var(--bg) 50%, transparent);
    }

    .composer {
      max-width: 980px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr auto auto auto;
      gap: 10px;
      align-items: end;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 22px;
      padding: 12px;
      box-shadow: var(--shadow);
    }

    textarea {
      min-height: 54px;
      max-height: 140px;
      resize: none;
      border: none;
      outline: none;
      background: transparent;
      color: var(--text);
      font: inherit;
      padding: 14px;
      line-height: 1.5;
    }

    textarea::placeholder {
      color: var(--muted);
    }

    .composer-btn {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--panel-soft);
      color: var(--text);
      cursor: pointer;
      transition: 0.2s;
      font-size: 18px;
    }

    .composer-btn:hover {
      background: #eff6ff;
    }

    body.dark .composer-btn:hover {
      background: #172033;
    }

    .send-btn {
      background: linear-gradient(135deg, var(--primary), var(--primary-dark));
      color: white;
      border: none;
    }

    .stop-btn {
      display: none;
      background: linear-gradient(135deg, #ef4444, #f97316);
      color: white;
      border: none;
    }

    .typing {
      display: inline-flex;
      gap: 6px;
      padding: 6px 0;
      align-items: center;
    }

    .typing span {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--primary);
      animation: blink 1.2s infinite;
    }

    .typing span:nth-child(2) { animation-delay: 0.15s; }
    .typing span:nth-child(3) { animation-delay: 0.30s; }

    @keyframes blink {
      0%, 80%, 100% { opacity: 0.25; transform: translateY(0); }
      40% { opacity: 1; transform: translateY(-5px); }
    }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 24px;
      transform: translateX(-50%) translateY(16px);
      background: var(--text);
      color: var(--panel);
      padding: 12px 16px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      opacity: 0;
      pointer-events: none;
      transition: 0.2s;
      z-index: 50;
    }

    body.dark .toast {
      background: #f8fafc;
      color: #0f172a;
    }

    .toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    @media (max-width: 980px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        display: none;
      }

      .suggestions {
        grid-template-columns: 1fr;
      }

      .bubble-wrap {
        max-width: 88%;
      }
    }

    @media (max-width: 640px) {
      .topbar {
        padding: 0 16px;
      }

      .welcome {
        padding: 30px 16px 12px;
      }

      .messages {
        padding: 10px 14px 170px;
      }

      .composer-wrap {
        padding: 14px;
      }

      .composer {
        grid-template-columns: 1fr auto;
      }

      .attach-btn,
      .theme-btn {
        display: none;
      }

      .bubble-wrap {
        max-width: 100%;
      }

      .avatar {
        display: none;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-logo">S</div>
        <div>
          <h1>StudyFlow AI</h1>
          <p>Clean AI study workspace</p>
        </div>
      </div>

      <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>

      <div class="sidebar-label">Recent Chats</div>
      <div class="session-list" id="sessionList"></div>

      <div class="sidebar-actions">
        <button class="side-action" onclick="downloadChat()">Download Current Chat</button>
        <button class="side-action" onclick="toggleTheme()">Toggle Theme</button>
        <button class="side-action" onclick="clearAllSessions()">Clear All Chats</button>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="topbar-left">
          <h2>StudyFlow Chat</h2>
          <p>Ask, learn, revise, and explore</p>
        </div>
        <div class="topbar-right">
          <div class="pill">{{ model_name }}</div>
          <button class="icon-btn" onclick="toggleTheme()" title="Theme">☾</button>
          <button class="icon-btn" onclick="newChat()" title="New Chat">＋</button>
        </div>
      </header>

      <section class="content">
        <div class="welcome" id="welcome">
          <h3>Learn smarter with <span>StudyFlow AI</span></h3>
          <p>
            A clean AI study assistant for explanations, coding help, summaries,
            preparation, and everyday learning support.
          </p>

          <div class="suggestions">
            <button class="suggestion-card" onclick="useSuggestion('Explain Python basics for a beginner with examples')">
              <b>Explain Python basics for a beginner with examples</b>
              <span>Start with programming concepts</span>
            </button>

            <button class="suggestion-card" onclick="useSuggestion('Give me a study plan to learn Flask from zero')">
              <b>Give a study plan to learn Flask from zero</b>
              <span>Create a structured roadmap</span>
            </button>

            <button class="suggestion-card" onclick="useSuggestion('Generate frontend developer interview questions and answers')">
              <b>Generate frontend developer interview questions and answers</b>
              <span>Practice for interviews</span>
            </button>

            <button class="suggestion-card" onclick="useSuggestion('Summarize machine learning in simple words')">
              <b>Summarize machine learning in simple words</b>
              <span>Understand a concept quickly</span>
            </button>
          </div>
        </div>

        <div class="messages" id="messages"></div>

        <div class="composer-wrap">
          <div class="composer">
            <textarea id="input" rows="1" maxlength="4000" placeholder="Ask anything..."></textarea>
            <button class="composer-btn attach-btn" onclick="showToast('File upload can be added later')" title="Attach">📎</button>
            <button class="composer-btn theme-btn" onclick="toggleTheme()" title="Theme">☾</button>
            <button class="composer-btn stop-btn" id="stopBtn" onclick="stopRequest()" title="Stop">■</button>
            <button class="composer-btn send-btn" id="sendBtn" onclick="sendMessage()" title="Send">➜</button>
          </div>
        </div>
      </section>
    </main>
  </div>

  <div class="toast" id="toast">Copied</div>

  <script>
    const input = document.getElementById('input');
    const messagesEl = document.getElementById('messages');
    const sessionListEl = document.getElementById('sessionList');
    const welcomeEl = document.getElementById('welcome');
    const sendBtn = document.getElementById('sendBtn');
    const stopBtn = document.getElementById('stopBtn');
    const toast = document.getElementById('toast');

    const STORE_KEY = 'studyflow_sessions_v1';
    const THEME_KEY = 'studyflow_theme';

    let sessions = [];
    let activeSessionId = null;
    let activeController = null;

    function makeId() {
      return 's_' + Date.now() + '_' + Math.random().toString(16).slice(2);
    }

    function nowTime() {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function renderMarkdown(text) {
      let safe = escapeHtml(text);
      safe = safe.replace(/```([\s\S]*?)```/g, function(match, code) {
        return '<pre><code>' + code.trim() + '</code></pre>';
      });
      safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
      safe = safe.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      safe = safe.replace(/\n/g, '<br>');
      return safe;
    }

    function saveSessions() {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        sessions: sessions,
        activeSessionId: activeSessionId
      }));
    }

    function loadSessions() {
      const raw = localStorage.getItem(STORE_KEY);

      if (!raw) {
        createSession(false);
        return;
      }

      try {
        const data = JSON.parse(raw);
        sessions = Array.isArray(data.sessions) ? data.sessions : [];
        activeSessionId = data.activeSessionId || null;

        if (!sessions.length) {
          createSession(false);
          return;
        }

        if (!sessions.some(s => s.id === activeSessionId)) {
          activeSessionId = sessions[0].id;
        }
      } catch (e) {
        sessions = [];
        createSession(false);
      }
    }

    function activeSession() {
      return sessions.find(s => s.id === activeSessionId);
    }

    function createSession(render = true) {
      const session = {
        id: makeId(),
        title: 'New Chat',
        createdAt: Date.now(),
        messages: []
      };
      sessions.unshift(session);
      activeSessionId = session.id;
      saveSessions();
      if (render) renderAll();
    }

    function newChat() {
      createSession(true);
      input.focus();
      showToast('New chat created');
    }

    function switchSession(id) {
      activeSessionId = id;
      saveSessions();
      renderAll();
    }

    function updateSessionTitle(session, text) {
      if (session.title === 'New Chat') {
        session.title = text.length > 36 ? text.slice(0, 36) + '...' : text;
      }
    }

    function renderSessionList() {
      if (!sessionListEl) return;

      sessionListEl.innerHTML = '';

      sessions.forEach(session => {
        const btn = document.createElement('button');
        btn.className = 'session-item' + (session.id === activeSessionId ? ' active' : '');
        btn.onclick = () => switchSession(session.id);

        btn.innerHTML = `
          <div class="session-item-title">${escapeHtml(session.title)}</div>
          <div class="session-item-meta">${session.messages.length} messages</div>
        `;

        sessionListEl.appendChild(btn);
      });
    }

    function renderMessages() {
      messagesEl.innerHTML = '';

      const session = activeSession();
      const list = session ? session.messages : [];

      welcomeEl.style.display = list.length ? 'none' : 'block';

      list.forEach(msg => {
        addMessageToDOM(msg.role, msg.content, msg.time, false);
      });

      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function renderAll() {
      renderSessionList();
      renderMessages();
    }

    function addMessageToDOM(role, text, time = nowTime(), allowCopy = true) {
      welcomeEl.style.display = 'none';

      const row = document.createElement('div');
      row.className = 'row ' + role;

      const avatar = document.createElement('div');
      avatar.className = 'avatar ' + (role === 'user' ? 'user' : 'bot');
      avatar.textContent = role === 'user' ? '👤' : 'AI';

      const wrap = document.createElement('div');
      wrap.className = 'bubble-wrap';

      const head = document.createElement('div');
      head.className = 'bubble-head';
      head.innerHTML = `<span>${role === 'user' ? 'You' : 'StudyFlow'} • ${escapeHtml(time)}</span>`;

      if (allowCopy) {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => copyText(text, copyBtn);
        head.appendChild(copyBtn);
      }

      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.innerHTML = role === 'assistant'
        ? renderMarkdown(text)
        : escapeHtml(text).replace(/\n/g, '<br>');

      wrap.appendChild(head);
      wrap.appendChild(bubble);

      if (role === 'user') {
        row.appendChild(wrap);
        row.appendChild(avatar);
      } else {
        row.appendChild(avatar);
        row.appendChild(wrap);
      }

      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;

      return row;
    }

    function addTyping() {
      const row = document.createElement('div');
      row.className = 'row assistant';
      row.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="bubble-wrap">
          <div class="bubble-head"><span>StudyFlow • ${nowTime()}</span></div>
          <div class="bubble">
            <div class="typing"><span></span><span></span><span></span></div>
          </div>
        </div>
      `;
      welcomeEl.style.display = 'none';
      messagesEl.appendChild(row);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return row;
    }

    async function copyText(text, btn) {
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = 'Copied';
        showToast('Message copied');
        setTimeout(() => btn.textContent = 'Copy', 1200);
      } catch (e) {
        showToast('Copy failed');
      }
    }

    function getApiMessages(session) {
      return session.messages.map(m => ({
        role: m.role,
        content: m.content
      })).slice(-14);
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text || sendBtn.disabled) return;

      let session = activeSession();

      if (!session) {
        createSession(false);
        session = activeSession();
      }

      input.value = '';
      autoResize();

      const userMsg = {
        role: 'user',
        content: text,
        time: nowTime()
      };

      session.messages.push(userMsg);
      updateSessionTitle(session, text);
      saveSessions();
      renderSessionList();
      addMessageToDOM('user', userMsg.content, userMsg.time);

      sendBtn.style.display = 'none';
      stopBtn.style.display = 'inline-block';
      activeController = new AbortController();

      const typing = addTyping();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: getApiMessages(session) }),
          signal: activeController.signal
        });

        const data = await res.json().catch(() => ({
          error: 'Server returned invalid JSON.'
        }));

        typing.remove();

        if (!res.ok || data.error) {
          addMessageToDOM('assistant', '⚠ Error: ' + (data.error || 'Request failed.'), nowTime());
          return;
        }

        const assistantMsg = {
          role: 'assistant',
          content: data.reply,
          time: nowTime()
        };

        session.messages.push(assistantMsg);
        saveSessions();
        addMessageToDOM('assistant', assistantMsg.content, assistantMsg.time);

      } catch (err) {
        typing.remove();

        if (err.name === 'AbortError') {
          addMessageToDOM('assistant', 'Request stopped.', nowTime());
        } else {
          addMessageToDOM('assistant', '⚠ Network error. Please check the Flask server.', nowTime());
        }

      } finally {
        sendBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        activeController = null;
        input.focus();
      }
    }

    function stopRequest() {
      if (activeController) activeController.abort();
    }

    function autoResize() {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 140) + 'px';
    }

    input.addEventListener('input', autoResize);

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    function useSuggestion(text) {
      input.value = text;
      autoResize();
      input.focus();
    }

    function downloadChat() {
      const session = activeSession();

      if (!session || !session.messages.length) {
        showToast('No chat to download');
        return;
      }

      let content = 'StudyFlow AI - ' + session.title + '\n';
      content += '====================================\n\n';

      session.messages.forEach(msg => {
        const role = msg.role === 'user' ? 'You' : 'StudyFlow';
        content += role + ' (' + msg.time + '):\n' + msg.content + '\n\n';
      });

      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = 'studyflow-chat.txt';
      a.click();

      URL.revokeObjectURL(url);
      showToast('Chat downloaded');
    }

    function clearAllSessions() {
      if (!confirm('Clear all saved chats in this browser?')) return;

      localStorage.removeItem(STORE_KEY);
      sessions = [];
      createSession(false);
      saveSessions();
      renderAll();
      showToast('All chats cleared');
    }

    function toggleTheme() {
      document.body.classList.toggle('dark');
      localStorage.setItem(THEME_KEY, document.body.classList.contains('dark') ? 'dark' : 'light');
    }

    function loadTheme() {
      const theme = localStorage.getItem(THEME_KEY);
      if (theme === 'dark') {
        document.body.classList.add('dark');
      }
    }

    function showToast(text) {
      toast.textContent = text;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1700);
    }

    loadTheme();
    loadSessions();
    renderAll();
    input.focus();
  </script>
</body>
</html>
"""

def clean_messages(messages):
    cleaned = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()
        if not content:
            continue

        cleaned.append({
            "role": role,
            "content": content
        })

    return cleaned[-14:]


def call_groq(messages):
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found in .env file!")

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload_data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are StudyFlow AI, a helpful AI study assistant. Give clear, simple, beginner-friendly answers. Use examples when useful."
            }
        ] + clean_messages(messages),
        "temperature": 0.7,
        "max_tokens": 1024
    }

    payload = json.dumps(payload_data).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "User-Agent": "studyflow-ai-assistant/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return data["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")

        try:
            error_json = json.loads(error_body)
            message = error_json.get("error", {}).get("message", error_body)
        except Exception:
            message = error_body

        raise Exception(f"Groq API error {e.code}: {message}")

    except urllib.error.URLError as e:
        raise Exception(f"Network error: {e.reason}")

    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


@app.route("/")
def index():
    return render_template_string(HTML, model_name=MODEL_NAME)


@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON request"}), 400

    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    try:
        reply = call_groq(messages)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "groq_key_loaded": bool(GROQ_API_KEY),
        "model": MODEL_NAME
    })


if __name__ == "__main__":
    print(f"✅ GROQ_API_KEY loaded: {'Yes' if GROQ_API_KEY else 'NO - Check your .env file!'}")
    print(f"🤖 Model: {MODEL_NAME}")
    print("🚀 Running at http://127.0.0.1:5000")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)