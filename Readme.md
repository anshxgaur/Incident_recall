![](Bottom_up.svg)

**Incident Memory** is an AI-powered incident response system that turns resolved incidents into searchable knowledge and uses that experience to help solve future incidents.

> **Every incident you resolve makes the next one easier.**

<p align="center">
  <img src="docs/demo.gif" width="900" alt="Incident Memory Demo"/>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-000000?style=for-the-badge\&logo=flask\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF4B4B?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?style=for-the-badge\&logo=google\&logoColor=white)
![Hindsight](https://img.shields.io/badge/Hindsight-Memory-8B5CF6?style=for-the-badge)

</p>

---

## 🧠 How It Works

```text
🚨 New Incident
      │
      ▼
🧬 Embed Incident
      │
      ▼
🔎 Search Qdrant
      │
      ▼
🧠 Retrieve Past Experience
      │
      ▼
🤖 Generate AI Fix
      │
      ▼
👨‍💻 Engineer Approves
      │
      ▼
💾 Store Resolution
      │
      ▼
🧠 Memory Gets Smarter
      │
      └───────────────↺
```

The system follows a simple **Search → Suggest → Resolve → Learn** loop.

---

## 🚨 Example

A new incident arrives:

```text
Checkout API returning 504s during traffic spike
```

The system searches its memory and might find:

```text
🔎 Similarity: 94.7%

Past Incident:
Database connection pool exhaustion

Previous Fix:
Increased connection pool + tuned timeout
```

The LLM then uses the retrieved incidents as evidence to generate a suggested resolution.

The engineer can **edit, approve, and save** the resolution.

That resolution becomes part of the system's memory.

---

## ⚡ Why It's Different

| Traditional Incident Response | Incident Memory        |
| ----------------------------- | ---------------------- |
| Search logs                   | 🔎 Search experience   |
| Static runbooks               | 🧠 Learned resolutions |
| Keyword matching              | 🧬 Semantic retrieval  |
| Human remembers               | 💾 System remembers    |
| Knowledge gets lost           | ♾️ Knowledge compounds |

---

## 🏗️ Architecture

```text
                         👨‍💻 Engineer
                              │
                              ▼
                    ┌──────────────────┐
                    │   Flask + HUD    │
                    └───────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        🧬 Embedding     🔎 Qdrant      🤖 LLM
        Gemini/OpenAI    Vector DB     Gemini/OpenAI
             │              │              │
             │              └──────┬───────┘
             │                     │
             ▼                     ▼
        ┌──────────┐         AI Suggestion
        │ Postgres │
        │  Source  │
        │ of Truth │
        └────┬─────┘
             │
             ▼
        🧠 Hindsight
        Long-term Memory
```

### Stack

* **Flask** — API + web application
* **PostgreSQL / Supabase** — structured source of truth
* **Qdrant** — semantic vector search
* **Gemini / OpenAI** — embeddings + LLM reasoning
* **Hindsight** — optional retain / recall / reflect memory
* **Tailwind CSS** — Agent Brain HUD

---

## 🎛️ Agent Brain HUD

The UI provides a futuristic incident command center with:

* 🚨 Incident intake
* ⚡ Animated execution trace
* 🤖 AI-generated fixes
* 🧠 Live memory bank
* 📊 Qdrant similarity scores
* 🗑️ Delete / restore
* 📦 Export / backup
* ⌘K command palette
* 🧠 Hindsight toggle
* 📡 Telemetry logs

---

## 🚀 Quickstart

### 1. Clone

```bash
git clone <your-repository-url>
cd incident-memory
```

### 2. Create environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

```env
DATABASE_URL=your_postgres_url

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key

GEMINI_API_KEY=your_gemini_key
```

Optional:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_key
HINDSIGHT_BANK_ID=your_bank_id
```

### 5. Seed memory

```bash
python new_ingest.py
```

### 6. Start

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🔌 API

| Method | Endpoint                      | Purpose                |
| ------ | ----------------------------- | ---------------------- |
| `GET`  | `/`                           | Agent Brain HUD        |
| `GET`  | `/api/incidents`              | List incidents         |
| `POST` | `/api/search`                 | Search + AI suggestion |
| `POST` | `/api/resolve`                | Resolve + learn        |
| `GET`  | `/api/export`                 | Export memory          |
| `POST` | `/api/import`                 | Restore memory         |
| `POST` | `/api/incidents/<id>/delete`  | Soft delete            |
| `POST` | `/api/incidents/<id>/restore` | Restore                |
| `POST` | `/api/incidents/<id>/purge`   | Permanent delete       |

---

## 🧪 Testing

### End-to-end memory test

```bash
python e2e_walkthrough.py
```

### Lifecycle tests

```bash
python test_memory_lifecycle.py
```

Tests include:

```text
Export → Import
Delete → Restore
Purge
Idempotency
ID sequence safety
```

### Hindsight wiring

```bash
python backend/hindsight/test_wiring.py
```

---

## 📁 Project Structure

```text
incident-memory/
│
├── app.py                    # Flask API + UI
├── new_ingest.py             # Ingestion + embeddings
├── query_incidents.py        # Semantic retrieval
├── suggest_fix.py            # LLM fix generation
├── resolve_incident.py       # Resolution write-back
├── memory_backup.py          # Backup / restore
│
├── backend/
│   └── hindsight/            # Long-term memory
│
├── templates/
│   └── index.html             # Agent Brain HUD
│
├── seed_incidents.json        # Seed incidents
├── e2e_walkthrough.py         # E2E verification
├── test_memory_lifecycle.py   # Lifecycle tests
└── requirements.txt
```

---

## 🧠 Hindsight Integration

Hindsight adds optional long-term experience storage:

```text
RETAIN
  ↓
RECALL
  ↓
REFLECT
  ↓
BETTER CONTEXT
  ↓
LLM
```

The core application continues working with **Postgres + Qdrant + LLM** even when Hindsight is unavailable.

---

## 🛣️ Roadmap

* [ ] Richer resolution outcomes
* [ ] Real/local Hindsight integration tests
* [ ] Qdrant integration tests
* [ ] Per-incident Hindsight memories in UI
* [ ] Improved experience schemas
* [ ] More incident scenarios

---

## 🎯 The Core Idea

```text
     INCIDENT
        ↓
     MEMORY
        ↓
    RETRIEVAL
        ↓
    AI REASONING
        ↓
    RESOLUTION
        ↓
   MEMORY GROWS
        ↓
     REPEAT ↺
```

> **Don't just build an AI that answers.
> Build an AI that remembers why the answer worked.**

---

<p align="center">

### 🚨 Incident → 🧠 Memory → 🤖 Reasoning → ✅ Resolution

**Every incident teaches the next one.**

⭐ Star the repository if you find the idea interesting.

</p>
