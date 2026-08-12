# Incident Memory — A Self-Improving Incident Response Memory

A compact, production-oriented demo that gives an on-call team an **AI-powered incident memory**. The system stores resolved incidents as semantically searchable vectors plus structured records, so every future incident is answered with evidence from the past — and every resolved incident makes the memory smarter.

The project demonstrates a complete "memory compounds" loop:

1. A **new incident** is described (in the UI or via the API).
2. Its text is **embedded** with the same model used at ingest time.
3. **Qdrant** returns the most semantically similar past incidents.
4. An **LLM** (Gemini or OpenAI) reads the current incident + the past matches and proposes a fix, citing which past incidents it matched on.
5. The engineer **edits/approves** the fix and marks the incident resolved.
6. The approved fix is **written back** to Postgres + Qdrant — the memory grew by one, and the next suggestion gets smarter.

An optional **Hindsight** layer adds long-term experience storage (retain / recall / reflect) so lessons persist beyond the vector index.

**Status:** core app complete and tested (search → suggest → resolve → learn, plus backup/restore and delete/undo lifecycle). The **Hindsight long-term memory layer is wired to the real `hindsight_client` SDK** (retain / recall / reflect with dedup) and runtime-guarded, so it works when configured and the app runs fine without it (see [Hindsight integration](#hindsight-integration)).

---

## Repository layout

| File / dir | Role |
|---|---|
| `app.py` | Flask web app: serves the UI and all HTTP API endpoints (search, resolve, export/import, delete/restore/purge). |
| `new_ingest.py` | Seeding pipeline: inserts `seed_incidents.json` into Postgres, embeds each incident, upserts vectors into Qdrant. Also owns shared DB/embedding/Qdrant setup used by every other module. |
| `query_incidents.py` | Retrieval helpers: embed a query → Qdrant semantic search → enrich hits with full Postgres records. |
| `suggest_fix.py` | LLM fix generation: builds a structured prompt (current incident + Qdrant matches + optional Hindsight memories/reflection) and calls Gemini or OpenAI. |
| `resolve_incident.py` | Write-back: stores an approved fix into Postgres + Qdrant with commit-after-upsert ordering, so the memory compounds. |
| `memory_backup.py` | Full snapshot export/import (rows + vectors + embedding metadata) with id-sequence re-sync. |
| `init_db.py` | Minimal one-off script to create the `incidents` schema. |
| `templates/index.html` | The "Agent Brain HUD" UI: intake form, live pipeline trace, AI fix box, memory bank, command palette, telemetry log, export button. |
| `backend/hindsight/` | Wired Hindsight long-term memory layer: config + SDK wrapper, `IncidentExperience` schema, retain (with dedup) / recall / reflect helpers, batch retain script, and `test_wiring.py` unit tests. |
| `seed_incidents.json` | 12 realistic seed incidents (payments, checkout, auth, database, cache, …) covering recurring failure patterns. |
| `e2e_walkthrough.py` | End-to-end test through the real API proving memory compounds (2 full cycles). |
| `test_memory_lifecycle.py` | Lifecycle tests: export/import, soft-delete, restore, purge, idempotency, id-sequence safety. |
| `incidents_backup.json` | A previously exported memory snapshot. |
| `detect_hindsight_sdk.py` | Diagnostic script that reports which Hindsight SDK modules are importable. |
| `backend/hindsight/test_wiring.py` | Unit tests for the Hindsight wiring (runs against a faked SDK — no network). |
| `document (1).pdf` | Project article: a ~1100-word technical overview of the system (generated PDF). |
| `.env.example` | Environment-variable template (copy to `.env`). ⚠️ It currently contains real-looking credentials — rotate/replace before sharing this repo. |

---

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │  Flask app (app.py) + Agent Brain HUD (UI)    │
                    └───────────────┬──────────────────────────────┘
                                    │
              embed                 │                     LLM prompt
   ┌─────────────────────┐          ▼          ┌──────────────────────┐
   │  Embedding (Gemini   │   ┌───────────┐    │  LLM (Gemini / OpenAI)│
   │  or OpenAI)          │   │ Qdrant    │    │  → suggested fix      │
   └─────────────────────┘   │ vectors   │    └──────────┬───────────┘
            ▲                └─────┬─────┘               │ approved fix
            │                      │                     ▼
   ┌────────┴─────────┐   ┌────────┴─────────┐   ┌───────────────┐
   │  Postgres        │   │  Qdrant          │   │  Hindsight    │
   │  (source of      │   │  (semantic       │   │  (long-term   │
   │   truth, rows)   │   │   similarity)    │   │   memory)     │
   └──────────────────┘   └──────────────────┘   └───────────────┘
```

- **Postgres** — primary source of truth for incident records (`incidents` table: title, description, root cause, resolution, service, severity, status, created_at). Supabase-compatible (`DATABASE_URL`).
- **Qdrant** — vector index (cosine similarity). Points are keyed by the same id as the Postgres rows so the two stores always stay addressable. The `incidents` collection holds 768-dim vectors from `gemini-embedding-001` (or 1536-dim from OpenAI's `text-embedding-3-small`).
- **LLM** — generates evidence-based fix suggestions. Gemini (`gemini-3.6-flash`, free tier) or OpenAI (`gpt-4.1-mini`). Provider auto-detected from keys in `.env`.
- **Hindsight (optional)** — persistent experience bank for retain/recall/reflect. Guarded so the app runs fine without it.

### Embedding & LLM providers

- Embeddings default to **Gemini** (free) and fall back to **OpenAI** if only `OPENAI_API_KEY` is set. Force with `EMBED_PROVIDER=gemini|openai`. Model names can be overridden (`GEMINI_EMBED_MODEL`).
- Generation mirrors this: `GEN_PROVIDER=gemini|openai` (default `auto`), models overridable via `GEN_LLM_MODEL` / `OPENAI_LLM_MODEL`.
- Transient embedding/LLM failures are retried with exponential backoff, and helpful troubleshooting hints are printed when keys, quotas, or retired model names cause failures.

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1. Configure .env (copy .env.example; add your keys)
#    - DATABASE_URL (Postgres / Supabase)
#    - QDRANT_URL (+ QDRANT_API_KEY for Qdrant Cloud)
#    - GEMINI_API_KEY (free, recommended) or OPENAI_API_KEY
#    - Optional: HINDSIGHT_API_URL (https://api.hindsight.vectorize.io for the cloud)
#                HINDSIGHT_API_KEY / HINDSIGHT_BANK_ID
#                HINDSIGHT_REFLECT_MISSION / HINDSIGHT_RETAIN_MISSION (bank missions)

# 2. Seed the memory (Postgres rows + Qdrant vectors)
python new_ingest.py                 # --check and --test-embed are safe dry-runs

# 3. Start the app
python app.py                        # http://127.0.0.1:5000  (--port 5001 to change)
```

Then use the UI to search, edit/approve an AI fix, and store it — watch the incident count tick up as the memory compounds.

### CLI tools

```bash
python query_incidents.py "payment service timing out during flash sale"   # search only
python suggest_fix.py "checkout 504s under traffic spike"                  # search + LLM fix
python suggest_fix.py --dry-run "payment api 504s"                          # prompt, no LLM call
python resolve_incident.py "db connection exhaustion" --resolution "bumped pool to 100"
python memory_backup.py export incidents_backup.json                        # full snapshot
python memory_backup.py import incidents_backup.json                        # restore (upsert)
python memory_backup.py check                                               # store counts
```

---

## API endpoints

| Method & path | Purpose |
|---|---|
| `GET /` | The Agent Brain HUD page. |
| `GET /api/incidents` | All incidents (newest first) + active/deleted counts. |
| `POST /api/search` | `{description, service?, severity?, top?, threshold?}` → ranked `matches` + LLM `suggestion` (+ optional `hindsight_memories`/`hindsight_reflection`). |
| `POST /api/resolve` | `{description, suggestion, service?, severity?, learn?}` → stores the fix; `learn: true` also retains into Hindsight. |
| `GET /api/export` | Download the full memory snapshot (rows + vectors + embedding metadata). |
| `POST /api/import` | Restore a snapshot (upsert/merge, never a wipe). |
| `POST /api/incidents/<id>/delete` | Soft delete: drops the Qdrant point, marks the row `deleted` (undoable). |
| `POST /api/incidents/<id>/restore` | Undo: re-embeds and re-upserts the point. |
| `POST /api/incidents/<id>/purge` | Permanent delete from both stores. |

Consistency notes: writes are ordered so the two stores can never silently desync in the dangerous direction (e.g. restore marks the row resolved *before* upserting the point; ingest upserts Qdrant *before* committing Postgres). Every module reuses the same `.env`-driven setup from `new_ingest.py`, so there is no duplicated connection/config code.

---

## The UI — Agent Brain HUD

A dark, glassmorphic single-page UI (`templates/index.html`, Tailwind CSS) with:

- **Incident Intake** — describe the issue (with a scanning-laser effect), pick service/severity, run a semantic search.
- **Memory Execution Trace** — an animated 4-step pipeline readout (embed → Hindsight recall → rerank context → LLM synthesis) with per-step timing.
- **AI Fix & Resolution** — the LLM suggestion with a "recalled fix injected" banner from the best past match; edit and store.
- **Memory Bank** — every incident with live similarity chips (real Qdrant scores), severity badges, filter, delete/restore.
- **Command palette (⌘K)**, **Export** button, telemetry log, toasts, and a Hindsight on/off toggle.

---

## Testing & verification

```bash
python e2e_walkthrough.py            # proves memory compounds across 2 real API cycles
python e2e_walkthrough.py --reset    # first removes UI-resolved rows, then runs
python test_memory_lifecycle.py      # export/import, delete/restore/purge, idempotency
python memory_backup.py check        # Postgres vs Qdrant counts
```

`e2e_walkthrough.py` runs two cycles (payments/flash-sale → related checkout incident, and notification OOMKill → related reporting OOMKill). Each cycle resolves an incident and then verifies the very next related query retrieves and cites it. `test_memory_lifecycle.py` covers snapshot export/import (with original ids and vectors), soft-delete, restore, purge, import idempotency, and `SERIAL` sequence safety.

---

## Hindsight integration

The long-term memory layer lives in `backend/hindsight/` and is wired to the installed `hindsight_client` SDK (`Hindsight(base_url=…, api_key=…)` with `retain` / `recall` / `reflect`):

- `client.py` — `HindsightConfig` (kwargs override env: `HINDSIGHT_API_URL`, `HINDSIGHT_API_KEY`, `HINDSIGHT_BANK_ID`) + `HindsightClientWrapper` (`available()`, `connect()` with best-effort bank creation, `retain()` / `recall()` / `reflect()`). Degrades to no-op when the SDK or config is missing.
- `schemas.py` — `IncidentExperience` dataclass (incident_id, title, service, severity, status, description, root cause, resolution, outcome, lesson) + `to_dict()`.
- `retain.py` — `retain_experience()` renders the experience as natural-language memory content **plus structured metadata**, tags it (`incident`, `service:*`, `severity:*`), and **dedupes by retaining each incident under `document_id=incident-<id>` with `update_mode="replace"`** — re-resolving an incident replaces its memory instead of duplicating it.
- `recall.py` — `recall_memories(client, description, top_k)` calls `client.recall(...)` and maps results onto the fields the LLM prompt expects (incident_id, service, severity, outcome, root cause, resolution, lesson).
- `reflect.py` — `reflect_memories(client, query)` calls `client.reflect(...)` (query-driven, with `include_facts=True`) and returns `{ok, insights, based_on}` for the prompt.
- `retain_historical.py` — batch script that loads all non-deleted incidents from Postgres and retains them (`--dry-run`, `--no-dedup` options).
- `test_wiring.py` — 16 unit tests that verify the wiring against a faked SDK (no network): `python backend/hindsight/test_wiring.py`.

The `/api/search` endpoint recalls Hindsight memories and, when ≥ 2 memories match, asks Hindsight to reflect and appends the synthesized insights to the LLM prompt. `/api/resolve` retains when the UI's Hindsight toggle is ON (`learn: true`). All Hindsight calls are wrapped in `try/except`, so the core search/suggest/resolve loop keeps working with Qdrant + LLM even when Hindsight is down.

**Going live:** set `HINDSIGHT_API_URL=https://api.hindsight.vectorize.io`, a real `HINDSIGHT_API_KEY` (cloud credits: promo code `MEMHACK89`), and your `HINDSIGHT_BANK_ID` in `.env`, then run `python backend/hindsight/retain_historical.py` to seed the bank, and restart the app. The bank is auto-created with incident-response retain/reflect missions.

---

## Known gaps & next steps

- **MEDIUM** — Capture richer resolution outcomes (failed / partial / success) at resolve time and propagate them to Hindsight (schema already supports `outcome`).
- **MEDIUM** — Add integration tests that run against a real/local Hindsight bank (current tests use a faked SDK), and tests that mock Qdrant.
- **LOW** — Expose per-incident Hindsight memories in the UI beyond the count badge.
- **LOW** — Document the exact Hindsight SDK adapter mapping and an example bank schema.

---

## Contact / author

This README was updated to reflect the current state of the project. Want the Hindsight layer completed, more seed scenarios, or UI/API polish? Just say which to implement next.
