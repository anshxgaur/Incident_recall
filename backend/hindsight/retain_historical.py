"""Batch script: retain all historical incidents from Postgres into Hindsight.

Retains every active incident from the Postgres ``incidents`` table as a
Hindsight memory, using the same document-id + replace dedup as the live
``/api/resolve`` path, so re-running is safe.

Usage (with .env configured for both Postgres and Hindsight):
    python backend/hindsight/retain_historical.py
    python backend/hindsight/retain_historical.py --no-dedup
    python backend/hindsight/retain_historical.py --dry-run   # no writes
"""
import argparse
import os
import sys

# Make the project root importable regardless of how the script is invoked.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Load the project's .env into os.environ (same as new_ingest.py does for the app).
from dotenv import load_dotenv

load_dotenv(override=True)

from backend.hindsight.client import HindsightConfig, HindsightClientWrapper
from backend.hindsight.retain import retain_experience
from backend.hindsight.schemas import IncidentExperience


def load_incidents() -> list[dict]:
    """Read all non-deleted incidents from Postgres (reuses the app's DB setup)."""
    from new_ingest import connect_db

    with connect_db() as conn:
        rows = conn.execute(
            "SELECT id, title, description, root_cause, resolution, service, "
            "severity, status FROM incidents WHERE status <> 'deleted' "
            "ORDER BY id"
        ).fetchall()
    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "root_cause": r[3],
            "resolution": r[4],
            "service": r[5],
            "severity": r[6],
            "status": r[7],
        }
        for r in rows
    ]


def retain_historical_incidents(
    client,
    incidents: list[dict],
    dedup: bool = True,
) -> dict:
    """Retain a list of incident dicts. Returns {retained, skipped, total}."""
    if client is None or not client.available():
        return {"retained": 0, "skipped": len(incidents), "total": len(incidents)}

    retained = 0
    skipped = 0
    for inc in incidents:
        exp = IncidentExperience(
            incident_id=str(inc.get("id")),
            title=inc.get("title"),
            service=inc.get("service"),
            severity=inc.get("severity"),
            status=inc.get("status") or "resolved",
            description=inc.get("description"),
            root_cause=inc.get("root_cause"),
            resolution=inc.get("resolution"),
            outcome="resolved",
        )
        result = retain_experience(client, exp, dedup=dedup)
        if result.get("retained"):
            retained += 1
            print(f"  retained incident #{inc.get('id')}: {inc.get('title')}")
        else:
            skipped += 1
            print(
                f"  skipped incident #{inc.get('id')}: {inc.get('title')} "
                f"({result.get('reason') or result.get('ok')})"
            )
    return {"retained": retained, "skipped": skipped, "total": len(incidents)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Retain historical incidents from Postgres into Hindsight."
    )
    parser.add_argument(
        "--no-dedup", action="store_true",
        help="append instead of replace when an incident is retained again",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="print what would be retained without calling Hindsight",
    )
    args = parser.parse_args()

    config = HindsightConfig()
    if not config.enabled:
        print(
            "Hindsight is not configured. Set HINDSIGHT_API_URL, "
            "HINDSIGHT_API_KEY and HINDSIGHT_BANK_ID in .env"
        )
        return 1

    try:
        incidents = load_incidents()
    except SystemExit as exc:
        print(f"Could not load incidents from Postgres: {exc}")
        return 1

    print(f"Loaded {len(incidents)} incident(s) from Postgres.")

    client = HindsightClientWrapper(config)
    if not client.available():
        print(f"Hindsight client unavailable: {client.error}")
        return 1

    if args.dry_run:
        for inc in incidents:
            print(f"  would retain incident #{inc.get('id')}: {inc.get('title')}")
        print("Dry run: nothing was written.")
        return 0

    if client.connect():
        print(f"Connected to Hindsight bank '{config.bank_id}'.")
    counts = retain_historical_incidents(client, incidents, dedup=not args.no_dedup)
    print(
        f"Done: {counts['retained']} retained, {counts['skipped']} skipped "
        f"(of {counts['total']})."
    )
    client.close()  # clean up the SDK's HTTP session
    return 0


if __name__ == "__main__":
    sys.exit(main())
