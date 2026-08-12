# 🚨 Incident Memory

### Your infrastructure has seen the problem before.

**Incident Memory** is an AI-powered incident response system that remembers how previous incidents were solved and uses that experience to help engineers resolve future incidents faster.

> **Every incident you resolve becomes knowledge for the next incident.**

<p align="center">
  <img src="docs/demo.gif" width="950" alt="Incident Memory Demo"/>
</p>

<p align="center">
  <b>Incident → Retrieve → Reason → Resolve → Learn → Repeat</b>
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-000000?style=for-the-badge\&logo=flask\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Source_of_Truth-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_Memory-FF4B4B?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?style=for-the-badge\&logo=google\&logoColor=white)
![Hindsight](https://img.shields.io/badge/Hindsight-Long_Term_Memory-8B5CF6?style=for-the-badge)

</p>

---

# 🧠 The Idea

Most incident-response systems can tell you **what is happening**.

Incident Memory tries to answer a more useful question:

> **"Have we seen this before, and what worked?"**

Instead of treating every incident as a completely new problem, the system turns resolved incidents into searchable experience.

When a new incident arrives:

```text
             🚨 NEW INCIDENT
                    │
                    ▼
             🧬 EMBEDDING
                    │
                    ▼
             🔎 QDRANT SEARCH
                    │
                    ▼
          🧠 PAST EXPERIENCE
                    │
                    ▼
              🤖 LLM REASONING
                    │
                    ▼
             🛠️ SUGGESTED FIX
                    │
                    ▼
             👨‍💻 HUMAN REVIEW
                    │
                    ▼
              ✅ RESOLUTION
                    │
                    ▼
          💾 WRITE BACK TO MEMORY
                    │
                    ▼
          🧠 MEMORY GETS SMARTER
                    │
                    └───────────────↺
```

This is the **memory-compounding loop**.

---

# 🔥 Memory Compounds

The core system follows six steps:

| Step                 | What happens                                                 |
| -------------------- | ------------------------------------------------------------ |
| 🚨 **1. Incident**   | A new incident is submitted through the UI or API            |
| 🧬 **2. Embed**      | The incident is converted into a semantic vector             |
| 🔎 **3. Retrieve**   | Qdrant searches for similar historical incidents             |
| 🤖 **4. Reason**     | Gemini or OpenAI generates an evidence-based fix             |
| 👨‍💻 **5. Approve** | An engineer reviews, edits, and approves the suggestion      |
| 🧠 **6. Learn**      | The approved resolution is written back to Postgres + Qdrant |

So the system doesn't simply **solve incidents**.

It **learns from solved incidents**.

```text
Incident #001
     │
     ▼
Resolution #001
     │
     ▼
   MEMORY
     │
     ▼
Incident #002
     │
     ├── retrieves #001
     │
     ▼
Better Resolution #002
     │
     ▼
   MEMORY++
     │
     ▼
Incident #003
     │
     ├── retrieves #001
     ├── retrieves #002
     │
     ▼
Even Better Resolution
```

---

# 🚨 See It Through a Real Incident

Imagine the checkout service suddenly starts returning `504` errors during a traffic spike.

### 01 — Incident arrives

```text
┌────────────────────────────────────────────────────┐
│ 🚨 NEW INCIDENT                                    │
├────────────────────────────────────────────────────┤
│ Checkout API returning 504s during traffic spike   │
│                                                    │
│ Service   : checkout                               │
│ Severity  : CRITICAL                               │
└───────────────────────────┬────────────────────────┘
                            │
                            ▼
```

### 02 — The system searches its memory

```text
┌────────────────────────────────────────────────────┐
│ 🔎 MEMORY SEARCH                                   │
├────────────────────────────────────────────────────┤
│ Searching Qdrant...                                │
│                                                    │
│ Similar Incident #42                               │
│ Similarity: 94.7%                                  │
│                                                    │
│ Root Cause:                                        │
│ DB connection pool exhaustion                      │
│                                                    │
│ Previous Resolution:                               │
│ Increased pool size + tuned connection timeout    │
└───────────────────────────┬────────────────────────┘
                            │
                            ▼
```

### 03 — AI reasons over the evidence

```text
┌────────────────────────────────────────────────────┐
│ 🤖 AI SUGGESTION                                   │
├────────────────────────────────────────────────────┤
│ Increase the DB connection pool and tune the       │
│ connection timeout based on the current traffic   │
│ characteristics.                                  │
│                                                    │
│ Evidence:                                          │
│ • Incident #42                                    │
│ • Incident #17                                    │
└───────────────────────────┬────────────────────────┘
                            │
                            ▼
```

### 04 — Engineer approves

```text
┌────────────────────────────────────────────────────┐
│ 👨‍💻 HUMAN REVIEW                                   │
├────────────────────────────────────────────────────┤
│ [ Edit Fix ]                    [ Approve & Learn ]│
└───────────────────────────┬────────────────────────┘
                            │
                            ▼
```

### 05 — The system learns

```text
             POSTGRES
                 │
                 ├── Incident record
                 │
                 ▼
              QDRANT
                 │
                 └── New vector
                       │
                       ▼
                🧠 MEMORY++
```

The next similar incident now has **one more piece of experience to retrieve**.

---

# ⚡ Why Incident Memory?

Traditional incident tooling often revolves around logs, alerts, dashboards, and static runbooks.

Incident Memory focuses on **experience**.

| Traditional Approach               | Incident Memory                     |
| ---------------------------------- | ----------------------------------- |
| Search logs                        | 🔎 Search experience                |
| Static runbooks                    | 🧠 Learned resolutions              |
| Keyword matching                   | 🧬 Semantic similarity              |
| Human remembers solutions          | 💾 System remembers                 |
| Knowledge disappears with people   | ♾️ Knowledge persists               |
| Every incident starts from scratch | 🔄 Every incident improves the next |

### The fundamental loop

```text
RESOLUTION
    ↓
MEMORY
    ↓
RETRIEVAL
    ↓
BETTER SUGGESTION
    ↓
NEW RESOLUTION
    ↓
MORE MEMORY
```

> **The system gets more useful as it gets used.**

---

# 🏗️ Architecture

```text
                              ┌────────────────────────┐
                              │      👨‍💻 ENGINEER      │
                              │                        │
                              │   Agent Brain HUD      │
                              └────────────┬───────────┘
                                           │
                                           ▼
                              ┌────────────────────────┐
                              │       FLASK APP         │
                              │        app.py           │
                              │                        │
                              │   UI + REST API        │
                              └───────┬────────┬────────┘
                                      │        │
                         ┌────────────┘        └─────────────┐
                         ▼                                  ▼
                ┌────────────────┐                 ┌────────────────┐
                │  🧬 EMBEDDING  │                 │   🤖 LLM       │
                │                │                 │                │
                │ Gemini/OpenAI  │                 │ Gemini/OpenAI  │
                └───────┬────────┘                 └───────▲────────┘
                        │                                  │
                        ▼                                  │
                ┌────────────────┐                         │
                │    🔎 QDRANT   │─────────────────────────┘
                │                │
                │ Vector Memory  │
                │ Semantic Search │
                └───────┬────────┘
                        │
                        │
                        ▼
                ┌────────────────┐
                │  🗄️ POSTGRES   │
                │                │
                │ Source of Truth│
                └───────┬────────┘
                        │
                        ▼
                ┌────────────────┐
                │ 🧠 HINDSIGHT    │
                │                │
                │ Long-Term      │
                │ Experience     │
                └────────────────┘
```

---

# 🧩 The Memory Stack

| Layer               | Technology       | Responsibility                 |
| ------------------- | ---------------- | ------------------------------ |
| 🎨 Interface        | Flask + Tailwind | Agent Brain HUD                |
| 🧬 Embeddings       | Gemini / OpenAI  | Convert incidents into vectors |
| 🔎 Vector Search    | Qdrant           | Semantic similarity retrieval  |
| 🗄️ Database        | PostgreSQL       | Source of truth                |
| 🤖 Reasoning        | Gemini / OpenAI  | Generate evidence-based fixes  |
| 🧠 Long-Term Memory | Hindsight        | Retain / Recall / Reflect      |

---

# 🗄️ Data Flow

The system maintains two complementary forms of memory.

### PostgreSQL

The structured source of truth.

Stores:

```text
incident
├── title
├── description
├── root cause
├── resolution
├── service
├── severity
├── status
└── created_at
```

### Qdrant

The semantic memory layer.

Each incident is embedded into a vector and stored in the `incidents` collection.

Points use the same IDs as PostgreSQL records, keeping both stores addressable.

### Hindsight

The optional long-term experience layer.

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

---

# 🎛️ Agent Brain HUD

The UI is designed as an **incident command center**, rather than a basic CRUD dashboard.

The current interface includes:

```text
┌─────────────────────────────────────────────────────────┐
│                    AGENT BRAIN HUD                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🚨 INCIDENT INTAKE                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Describe the incident...                          │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ⚡ MEMORY EXECUTION TRACE                              │
│                                                         │
│  [EMBED] → [RECALL] → [RERANK] → [SYNTHESIZE]          │
│                                                         │
│  🤖 AI FIX                                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ Suggested resolution...                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  🧠 MEMORY BANK                                         │
│                                                         │
│  Incident #42      94.7%      CRITICAL                 │
│  Incident #17      89.2%      HIGH                     │
│  Incident #08      84.6%      MEDIUM                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### UI capabilities

* 🚨 **Incident Intake** — describe an issue and select service/severity
* 🧬 **Scanning-Laser Effect** — visual feedback during processing
* ⚡ **Memory Execution Trace** — animated pipeline stages
* 🤖 **AI Fix & Resolution** — evidence-backed LLM suggestion
* 🧠 **Memory Bank** — incidents with real Qdrant similarity scores
* 🗑️ **Delete / Restore** — incident lifecycle management
* ⌘K **Command Palette**
* 📡 **Telemetry Log**
* 📦 **Export**
* 🧠 **Hindsight Toggle**
* 🔔 **Toasts and live feedback**

---

# 🧬 Embedding & LLM Providers

The project supports both Gemini and OpenAI.

### Embeddings

Gemini is the default provider.

```text
Gemini
   │
   ├── available
   │
   ▼
gemini-embedding-001
```

OpenAI can be used as an alternative.

```text
EMBED_PROVIDER=gemini
```

or

```text
EMBED_PROVIDER=openai
```

### Generation

The LLM provider can also be selected independently.

```text
GEN_PROVIDER=auto
```

Available options:

```text
gemini
openai
auto
```

Models can be overridden through environment variables.

Transient embedding and LLM failures are retried with exponential backoff, with troubleshooting hints for missing keys, quotas, and retired model names.

---

# 🚀 Quickstart

## 01 — Clone the repository

```bash
git clone <your-repository-url>
cd incident-memory
```

---

## 02 — Create a virtual environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 03 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## 04 — Configure environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Configure:

```env
DATABASE_URL=your_postgres_or_supabase_url

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

GEMINI_API_KEY=your_gemini_key
```

Optional Hindsight configuration:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_key
HINDSIGHT_BANK_ID=your_bank_id

HINDSIGHT_REFLECT_MISSION=your_reflect_mission
HINDSIGHT_RETAIN_MISSION=your_retain_mission
```

> ⚠️ Never commit your real `.env` file or API keys.

---

# 🌱 Seed the Memory

Load the initial incident knowledge:

```bash
python new_ingest.py
```

Safe checks:

```bash
python new_ingest.py --check
```

Embedding test:

```bash
python new_ingest.py --test-embed
```

This pipeline:

```text
seed_incidents.json
        │
        ▼
   PostgreSQL
        │
        ├──────────────┐
        │              │
        ▼              ▼
   Incident rows    Embeddings
                       │
                       ▼
                    Qdrant
```

---

# ⚡ Start the Brain

```bash
python app.py
```

Default:

```text
http://127.0.0.1:5000
```

To change the port:

```bash
python app.py --port 5001
```

Then open the Agent Brain HUD.

> 🧠 **Your incident memory is online.**

---

# 🧪 Try It From the CLI

### Search historical incidents

```bash
python query_incidents.py \
  "payment service timing out during flash sale"
```

### Search + generate an AI fix

```bash
python suggest_fix.py \
  "checkout 504s under traffic spike"
```

### Preview the prompt without calling the LLM

```bash
python suggest_fix.py \
  --dry-run \
  "payment api 504s"
```

### Resolve an incident

```bash
python resolve_incident.py \
  "db connection exhaustion" \
  --resolution "bumped pool to 100"
```

### Export memory

```bash
python memory_backup.py export incidents_backup.json
```

### Restore memory

```bash
python memory_backup.py import incidents_backup.json
```

### Check store counts

```bash
python memory_backup.py check
```

---

# 🔌 API

The Flask application exposes the complete incident-memory lifecycle.

| Method | Endpoint                      | Purpose                         |
| ------ | ----------------------------- | ------------------------------- |
| `GET`  | `/`                           | Agent Brain HUD                 |
| `GET`  | `/api/incidents`              | Retrieve incidents + counts     |
| `POST` | `/api/search`                 | Semantic search + AI suggestion |
| `POST` | `/api/resolve`                | Store approved resolution       |
| `GET`  | `/api/export`                 | Export full memory snapshot     |
| `POST` | `/api/import`                 | Restore/merge snapshot          |
| `POST` | `/api/incidents/<id>/delete`  | Soft delete                     |
| `POST` | `/api/incidents/<id>/restore` | Restore incident                |
| `POST` | `/api/incidents/<id>/purge`   | Permanently delete              |

### Search

```json
{
  "description": "checkout service returning 504s",
  "service": "checkout",
  "severity": "critical",
  "top": 5,
  "threshold": 0.75
}
```

Returns:

```text
matches
   +
suggestion
   +
optional Hindsight memories
   +
optional Hindsight reflection
```

### Resolve

```json
{
  "description": "checkout service returning 504s",
  "suggestion": "Increase DB connection pool...",
  "service": "checkout",
  "severity": "critical",
  "learn": true
}
```

With:

```text
learn = true
```

the approved experience can also be retained in Hindsight.

---

# 🔐 Consistency & Write Ordering

The system intentionally controls the order in which data is written to Postgres and Qdrant.

The goal is to prevent dangerous silent desynchronization.

```text
INGEST

Incident
   │
   ▼
Qdrant Upsert
   │
   ▼
Postgres Commit
```

Restore operations use an ordering that prevents the database from becoming resolved before the vector has been restored.

Every module reuses the same `.env`-driven database, embedding, and Qdrant setup from `new_ingest.py`.

This avoids duplicated connection/configuration logic.

---

# 🧠 Hindsight — Long-Term Experience

Hindsight is an optional long-term memory layer.

While Qdrant handles semantic similarity over incident vectors, Hindsight provides:

```text
RETAIN
  ↓
RECALL
  ↓
REFLECT
```

The integration lives inside:

```text
backend/hindsight/
```

### Components

| File                   | Responsibility                        |
| ---------------------- | ------------------------------------- |
| `client.py`            | Hindsight configuration + SDK wrapper |
| `schemas.py`           | `IncidentExperience` schema           |
| `retain.py`            | Store incident experience             |
| `recall.py`            | Retrieve relevant memories            |
| `reflect.py`           | Generate higher-level insights        |
| `retain_historical.py` | Batch historical retention            |
| `test_wiring.py`       | SDK wiring tests                      |

---

# 🧠 IncidentExperience

The experience schema contains:

```text
IncidentExperience
├── incident_id
├── title
├── service
├── severity
├── status
├── description
├── root cause
├── resolution
├── outcome
└── lesson
```

Experiences are stored with structured metadata and tags such as:

```text
incident
service:checkout
severity:critical
```

Retention is deduplicated using:

```text
document_id = incident-<id>
```

and:

```text
update_mode = replace
```

So resolving the same incident again updates its memory instead of creating unnecessary duplicates.

---

# 🔎 Hindsight Recall

During `/api/search`:

```text
New Incident
     │
     ├───────────────┐
     ▼               ▼
  Qdrant          Hindsight
     │               │
     │               ▼
     │            Memories
     │               │
     └───────┬───────┘
             ▼
        LLM Context
             │
             ▼
       AI Suggestion
```

When enough memories match, Hindsight can also perform reflection and provide synthesized insights to the LLM prompt.

All Hindsight calls are guarded so the core system still works when Hindsight is unavailable.

---

# 🧪 Testing & Verification

The project includes end-to-end and lifecycle verification.

### End-to-end memory compounding

```bash
python e2e_walkthrough.py
```

This proves the system can complete multiple incident cycles and retrieve the previous resolution for a related future incident.

Reset UI-resolved rows first:

```bash
python e2e_walkthrough.py --reset
```

---

### Lifecycle tests

```bash
python test_memory_lifecycle.py
```

Covers:

```text
Export
Import
Soft Delete
Restore
Purge
Idempotency
ID Sequence Safety
```

---

### Store consistency

```bash
python memory_backup.py check
```

---

### Hindsight wiring

```bash
python backend/hindsight/test_wiring.py
```

The Hindsight wiring tests run against a faked SDK and do not require network access.

---

# 🔄 End-to-End Verification

The walkthrough verifies the actual memory-compounding behavior.

### Cycle 1

```text
Payment / Flash Sale Incident
          │
          ▼
       Resolve
          │
          ▼
       Store
          │
          ▼
        MEMORY
```

### Cycle 2

```text
Related Checkout Incident
          │
          ▼
   Search Existing Memory
          │
          ▼
Retrieve Previous Resolution
          │
          ▼
       AI Suggestion
          │
          ▼
        Resolve
```

The same concept is tested with notification and reporting OOMKill scenarios.

---

# 💾 Backup & Recovery

Incident Memory supports full memory snapshots.

```text
Postgres rows
      +
Qdrant vectors
      +
Embedding metadata
      ↓
 incidents_backup.json
```

Export:

```bash
python memory_backup.py export incidents_backup.json
```

Restore:

```bash
python memory_backup.py import incidents_backup.json
```

The restore process performs upserts rather than wiping the existing store.

ID sequences are also re-synchronized for safety.

---

# 🗑️ Incident Lifecycle

Incidents support a complete lifecycle:

```text
              ACTIVE
                │
                ▼
           SOFT DELETE
                │
        ┌───────┴───────┐
        ▼               ▼
     RESTORE           PURGE
        │               │
        ▼               ▼
      ACTIVE        PERMANENTLY
                     DELETED
```

### Soft delete

Removes the Qdrant point and marks the database record as deleted.

### Restore

Re-embeds the incident and restores its Qdrant vector.

### Purge

Permanently removes the incident from both stores.

---

# 📁 Project Structure

```text
incident-memory/
│
├── app.py
│   └── Flask application, UI and API endpoints
│
├── new_ingest.py
│   └── Seed ingestion + shared DB/embedding/Qdrant setup
│
├── query_incidents.py
│   └── Semantic incident retrieval
│
├── suggest_fix.py
│   └── LLM-powered fix generation
│
├── resolve_incident.py
│   └── Resolution write-back / learning
│
├── memory_backup.py
│   └── Export / import / consistency checks
│
├── init_db.py
│   └── Database schema initialization
│
├── templates/
│   └── index.html
│       └── Agent Brain HUD
│
├── backend/
│   └── hindsight/
│       ├── client.py
│       ├── schemas.py
│       ├── retain.py
│       ├── recall.py
│       ├── reflect.py
│       ├── retain_historical.py
│       └── test_wiring.py
│
├── seed_incidents.json
│   └── Initial incident knowledge
│
├── e2e_walkthrough.py
│   └── End-to-end memory-compounding test
│
├── test_memory_lifecycle.py
│   └── Backup/delete/restore lifecycle tests
│
├── incidents_backup.json
│   └── Example memory snapshot
│
├── detect_hindsight_sdk.py
│   └── Hindsight SDK diagnostics
│
├── requirements.txt
│
├── .env.example
│
└── README.md
```

---

# 🛣️ Roadmap

The current implementation is functional, but there are several areas that can make the system stronger.

### 🔜 Next

* [ ] Capture richer resolution outcomes: failed / partial / success
* [ ] Propagate resolution outcomes into Hindsight
* [ ] Add integration tests against a real/local Hindsight bank
* [ ] Add Qdrant integration tests with mocked/vector-backed scenarios
* [ ] Expose per-incident Hindsight memories directly in the UI
* [ ] Document the exact Hindsight SDK adapter mapping
* [ ] Add an example Hindsight bank schema

---

# 📊 Current Capabilities

```text
                         INCIDENT MEMORY
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        🔎 SEARCH          🤖 SUGGEST       💾 LEARN
             │                │                │
             ▼                ▼                ▼
          QDRANT             LLM          POSTGRES
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                       🧠 HINDSIGHT
                              │
                              ▼
                       LONG-TERM MEMORY
```

### Core loop

**Search → Suggest → Resolve → Learn**

### Additional lifecycle

**Backup → Restore → Delete → Undo → Purge**

---

# 🌐 Going Live with Hindsight

Configure:

```env
HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_real_key
HINDSIGHT_BANK_ID=your_bank_id
```

Then seed historical incidents:

```bash
python backend/hindsight/retain_historical.py
```

Restart the application:

```bash
python app.py
```

The Hindsight layer is runtime-guarded, meaning the main application continues to operate with Qdrant + LLM even when Hindsight is not configured or unavailable.

---

# ⚠️ Security

Before sharing or deploying this project:

```text
.env
API KEYS
DATABASE CREDENTIALS
QDRANT API KEYS
HINDSIGHT API KEYS
```

should never be committed to Git.

Use:

```text
.env.example
```

for configuration templates.

> ⚠️ The original `.env.example` in this project contains real-looking credentials. Rotate and replace them before publishing the repository.

---

# 🎯 The One-Sentence Version

> **Incident Memory turns every solved production incident into searchable experience, allowing AI to use the past to solve the future.**

---

# 👨‍💻 Project

Built as a production-oriented demonstration of:

```text
Semantic Retrieval
        +
LLM Reasoning
        +
Vector Memory
        +
Structured Storage
        +
Long-Term Experience
        +
Human-in-the-Loop Learning
```

### The goal isn't just to build an AI that answers.

### The goal is to build an AI that **remembers why the answer worked.**

---

<p align="center">

## 🚨 INCIDENT → 🧠 MEMORY → 🤖 REASONING → ✅ RESOLUTION

### Every incident teaches the next one.

</p>

---

<p align="center">
  ⭐ If this project is interesting, consider starring the repository.
</p>
