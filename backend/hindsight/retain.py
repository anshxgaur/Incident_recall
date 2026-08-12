"""Retain helper for storing experiences in Hindsight long-term memory."""
from typing import Any, Dict

from backend.hindsight.schemas import IncidentExperience


def build_memory_text(experience: IncidentExperience) -> str:
    """Render an incident experience as natural-language memory content.

    Hindsight ingests text, decomposes it into facts, and searches it
    semantically — so a compact, structured narrative is ideal.
    """
    parts = []
    if experience.title:
        parts.append(f"Incident: {experience.title}")
    if experience.description:
        parts.append(f"Description: {experience.description}")
    if experience.root_cause:
        parts.append(f"Root cause: {experience.root_cause}")
    if experience.resolution:
        parts.append(f"Resolution: {experience.resolution}")
    if experience.lesson:
        parts.append(f"Lesson: {experience.lesson}")
    return "\n".join(parts) or "Incident experience"


def build_metadata(experience: IncidentExperience) -> Dict[str, str]:
    """Structured fields as string metadata so recall can return them to the
    LLM prompt without re-parsing the free text."""
    meta = {
        "incident_id": str(experience.incident_id or ""),
        "title": str(experience.title or ""),
        "service": str(experience.service or ""),
        "severity": str(experience.severity or ""),
        "status": str(experience.status or "resolved"),
        "outcome": str(experience.outcome or "resolved"),
        "root_cause": str(experience.root_cause or ""),
        "resolution": str(experience.resolution or ""),
        "lesson": str(experience.lesson or ""),
    }
    return {k: v for k, v in meta.items() if v}


def retain_experience(
    client,
    experience: IncidentExperience,
    dedup: bool = True,
) -> Dict[str, Any]:
    """Retain an incident experience in Hindsight.

    Deduplication: each experience is retained under ``document_id =
    incident-<incident_id>`` with ``update_mode="replace"``, so re-resolving or
    re-seeding the same incident replaces its memory instead of duplicating it.

    Args:
        client: HindsightClientWrapper instance (or None).
        experience: IncidentExperience instance to store.
        dedup: When True (default) re-retaining the same incident replaces the
            previous version rather than appending a duplicate.

    Returns:
        {'retained': bool, ...result}. Never raises.
    """
    if client is None or not client.available():
        return {"retained": False, "reason": "hindsight unavailable"}

    text = build_memory_text(experience)
    metadata = build_metadata(experience)

    tags = ["incident", "resolved"]
    if experience.service:
        tags.append(f"service:{experience.service}")
    if experience.severity:
        tags.append(f"severity:{experience.severity}")

    document_id = (
        f"incident-{experience.incident_id}"
        if experience.incident_id is not None
        else None
    )
    update_mode = "replace" if (dedup and document_id) else None

    result = client.retain(
        content=text,
        context="incident-memory",
        document_id=document_id,
        metadata=metadata,
        tags=tags,
        update_mode=update_mode,
    )
    if not result:
        return {"retained": False, "reason": "retain call failed"}
    # The SDK reports success via result["ok"]; never claim retention on failure.
    return {"retained": bool(result.get("ok", True)), **result}
