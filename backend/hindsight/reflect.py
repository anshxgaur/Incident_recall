"""Reflect helper for Hindsight learning (synthesized lessons)."""
from typing import Any, Dict, Optional


def reflect_memories(
    client,
    query: str,
    context: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Ask Hindsight to reflect over the bank's memories for a query.

    Args:
        client: HindsightClientWrapper instance (or None).
        query: The question/incident description to reflect on.
        context: Optional extra context.

    Returns:
        {'ok': True, 'insights': <markdown answer>, 'based_on': [...]} or
        None when Hindsight is unavailable/failed. Never raises.
    """
    if client is None or not client.available():
        return None
    try:
        return client.reflect(query, context=context)
    except Exception:  # noqa: BLE001 - non-fatal
        return None
