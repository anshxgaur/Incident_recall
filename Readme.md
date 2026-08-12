# Incident Memory — Demo

A compact incident memory demo that combines short-term semantic search (Qdrant) with a long-term learning layer (Hindsight). Designed as a minimal Flask app that demonstrates: ingesting incidents, semantic retrieval, LLM-driven fix suggestions, and retaining resolved incidents as long-term experiences.

Status: prototype — Hindsight integration scaffolding and runtime-guarded wrapper implemented. PHASES 1–10 completed; PHASE 11 verification in progress.

**Repository Layout**
- `app.py`: Flask app exposing `/api/search`, `/api/resolve`, incident lifecycle endpoints, and serves the UI.
- `suggest_fix.py`: CLI / server helper that builds the LLM prompt from Qdrant + Hindsight and calls the LLM to generate fixes.
- `new_ingest.py`: embedding + Qdrant & Postgres wiring (existing project code).
- `query_incidents.py`: Qdrant retrieval helpers.
- `resolve_incident.py`: write-back logic to Postgres + Qdrant.
- `templates/index.html`: UI — search, suggested fix, resolve, memory table.
- `backend/hindsight/`: Hindsight client wrapper, schemas, retain/recall/reflect helpers, and a retain-historical script.

**High-level architecture**

- Qdrant (semantic similarity) — store/search vectors for incidents.
- Postgres (primary source of truth) — incident rows, metadata.
- LLM (Gemini/OpenAI) — generate suggested fixes using combined context.
- Hindsight (optional long-term memory) — persistent experiences, recall and reflection to inform future suggestions.

Hindsight is an optional augmentation; the app degrades gracefully if the Hindsight SDK or config is absent.

**Key Hindsight files**
- `backend/hindsight/client.py` — `HindsightConfig`, `HindsightClientWrapper` (runtime-detecting, adapts to SDK shapes).
- `backend/hindsight/schemas.py` — `IncidentExperience` dataclass and `to_dict()`.
- `backend/hindsight/retain.py` — `retain_experience()` helper.
- `backend/hindsight/recall.py` — `recall_memories()` helper.
- `backend/hindsight/reflect.py` — reflect helper stub.
- `backend/hindsight/retain_historical.py` — batch retain script with dedup checks.

Environment variables

Required for core app (existing project):
- `DATABASE_URL` or `PGHOST`/`PGUSER`/`PGPASSWORD` etc. — Postgres connection
- `QDRANT_URL`, `QDRANT_API_KEY` — Qdrant connection (if applicable)
- `GEMINI_API_KEY` / `OPENAI_API_KEY` — LLM provider keys (one required for generation)

Hindsight-specific (optional):
- `HINDSIGHT_API_URL` — base URL for Hindsight API
- `HINDSIGHT_API_KEY` — API key for Hindsight
- `HINDSIGHT_BANK_ID` — bank/namespace id used by Hindsight

Important: Hindsight credentials are read server-side only and are never exposed to the frontend.

Quickstart (local)

1. Create a Python virtualenv and install dependencies (project has a minimal `requirements.txt`).

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows PowerShell
pip install -r requirements.txt
```

2. Configure environment variables (example `.env` or export in shell). For Hindsight tests set these only if you have a matching SDK/service:

```powershell
$env:HINDSIGHT_API_URL='https://api.hindsight.example'
$env:HINDSIGHT_API_KEY='YOUR_KEY'
$env:HINDSIGHT_BANK_ID='bank-id'
```

3. Start the app:

```bash
python app.py
```

4. Use the UI at `http://127.0.0.1:5000` to run searches, edit/accept suggestions, and mark incidents resolved.

Testing & verification (end-to-end)

- Quick Hindsight wrapper check (no SDK):

```bash
python backend/hindsight/test_client.py
```

- Quick Hindsight wrapper check (dummy env vars, SDK likely absent):

PowerShell:
```powershell
$env:HINDSIGHT_API_URL='https://example.local'
$env:HINDSIGHT_API_KEY='fake-key'
$env:HINDSIGHT_BANK_ID='bank-1'
python backend\hindsight\test_client.py
```

- Manual end-to-end sequence (recommended):

1. Start the server: `python app.py`.
2. TEST 1 — Search (captures Qdrant matches + Hindsight recall):

```powershell
$body = @'
{"description":"Database connection exhaustion","top":5,"threshold":0.2}
'@
curl -s -X POST http://127.0.0.1:5000/api/search -H "Content-Type: application/json" -d $body
```

3. TEST 2 — Resolve (send `learn: true` to retain into Hindsight):

```powershell
$body = @'
{"description":"Database connection exhaustion","suggestion":"Restart DB and check replication slots","service":"database","severity":"high","learn": true}
'@
curl -s -X POST http://127.0.0.1:5000/api/resolve -H "Content-Type: application/json" -d $body
```

4. TEST 3 — New similar incident: call `/api/search` again and verify `hindsight_memories` contains the retained item and that LLM output references it.

Notes about behavior, limitations, and known gaps

- Hindsight calls are optional and guarded. If the Hindsight SDK or configuration is missing, the app continues to use Qdrant + LLM only.
- `retain_historical.py` includes a deduplication step (it recalls by `incident_id` before retaining). However, the live `/api/resolve` retain path does **not** perform a dedup check — duplicates are possible on repeated resolve calls (frontend attempts to prevent double-clicks but that is not a strong guarantee).
- The current `/api/resolve` flow sets `outcome='resolved'` when retaining. There is no UI/API field to indicate failures or partial outcomes; the schema supports an `outcome` field but the UI must be extended to populate non-success outcomes.
- Reflection (synthesis) is invoked only when multiple memories are returned and the SDK exposes a reflect-like method. Otherwise reflection is skipped.

TODO / Next work (recommended)
- Add dedup protection to `/api/resolve` to match `retain_historical` logic (HIGH priority).
- Add structured outcome capture (failed/partial/success) at resolve time and propagate to Hindsight (MEDIUM).
- Add unit/integration tests that mock the Hindsight client for recall/reflect/retain behavior (MEDIUM).
- Add README documentation for Hindsight SDK adapters and mapping of expected SDK method names (LOW).

Contact / author

This README was generated by an automated assistant while integrating Hindsight as a long-term memory layer. If you want follow-up changes (tests, dedupe, outcome UI), tell me which to implement next.
