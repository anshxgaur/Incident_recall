"""Recall helper for Hindsight long-term memory."""
from typing import Any, Dict, List


def _result_to_dict(result) -> Dict[str, Any]:
    """Map a hindsight recall result object onto the dict shape the app's LLM
    prompt builder expects (see suggest_fix.build_user_prompt)."""
    metadata = dict(getattr(result, "metadata", None) or {})
    text = getattr(result, "text", "") or ""
    scores = getattr(result, "scores", None)
    final_score = getattr(scores, "final", None) if scores is not None else None
    return {
        "id": getattr(result, "id", None),
        "incident_id": (
            metadata.get("incident_id")
            or getattr(result, "document_id", None)
            or getattr(result, "id", None)
        ),
        "title": metadata.get("title"),
        "service": metadata.get("service"),
        "severity": metadata.get("severity"),
        "status": metadata.get("status"),
        "outcome": metadata.get("outcome"),
        "description": text,
        "symptom": text,
        "root_cause": metadata.get("root_cause"),
        "resolution": metadata.get("resolution"),
        "lesson": metadata.get("lesson"),
        "score": final_score if final_score is not None else None,
        "type": getattr(result, "type", None),
    }


def recall_memories(
    client,
    description: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Recall similar experiences from Hindsight for an incident description.

    Args:
        client: HindsightClientWrapper instance (or None).
        description: The incident description to search for.
        top_k: Maximum number of memories to return.

    Returns:
        List of dicts (see _result_to_dict). Empty when Hindsight is
        unavailable or the recall fails — never raises.
    """
    if client is None or not client.available():
        return []
    try:
        results = client.recall(description, top_k=top_k)
    except Exception:  # noqa: BLE001 - non-fatal
        return []
    return [_result_to_dict(r) for r in results][:top_k]
