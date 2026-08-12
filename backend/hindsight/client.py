"""Hindsight long-term memory client: config + runtime-detecting wrapper.

Wraps the real ``hindsight_client`` SDK (https://hindsight.vectorize.io) so the
rest of the app can use retain / recall / reflect through one small API. If the
SDK is not installed, or the environment is not configured, every method
degrades to a no-op so the core app keeps working without Hindsight.

Environment variables (server-side only, never exposed to the frontend):
    HINDSIGHT_API_URL    base URL of the Hindsight API (cloud:
                         https://api.hindsight.vectorize.io)
    HINDSIGHT_API_KEY    API key (sent as a Bearer token)
    HINDSIGHT_BANK_ID    memory bank (namespace) id
    HINDSIGHT_REFLECT_MISSION / HINDSIGHT_RETAIN_MISSION  optional bank missions
"""
import os

DEFAULT_REFLECT_MISSION = (
    "You are the long-term memory of an on-call incident response team. "
    "When asked about an incident, use past incidents, root causes, and "
    "resolutions stored in this bank to explain what likely happened and "
    "recommend concrete, evidence-based fixes."
)
DEFAULT_RETAIN_MISSION = (
    "Extract each incident's key details: what happened, the service and "
    "severity, the root cause, the resolution, and any lesson learned."
)


# Process-wide flag so bank creation is attempted once, not on every request
# (app.py builds a fresh wrapper per request; connect() is called each time).
_BANK_ENSURED = False


class HindsightConfig:
    """Configuration for the Hindsight API. Values come from constructor
    kwargs first, then environment variables."""

    def __init__(
        self,
        api_url=None,
        api_key=None,
        bank_id=None,
        reflect_mission=None,
        retain_mission=None,
        auto_create_bank=True,
    ):
        self.api_url = api_url or os.getenv("HINDSIGHT_API_URL")
        self.api_key = api_key or os.getenv("HINDSIGHT_API_KEY")
        self.bank_id = bank_id or os.getenv("HINDSIGHT_BANK_ID")
        self.reflect_mission = reflect_mission or os.getenv(
            "HINDSIGHT_REFLECT_MISSION", DEFAULT_REFLECT_MISSION
        )
        self.retain_mission = retain_mission or os.getenv(
            "HINDSIGHT_RETAIN_MISSION", DEFAULT_RETAIN_MISSION
        )
        self.auto_create_bank = auto_create_bank
        # A real API URL and a bank id are required; the API key is needed for
        # the cloud (the SDK accepts None for a local server).
        self.enabled = bool(self.api_url and self.bank_id)


class HindsightClientWrapper:
    """Runtime-detecting wrapper around the ``hindsight_client`` SDK.

    Attributes:
        config: the HindsightConfig in use.
        client: the underlying ``hindsight_client.Hindsight`` instance, or
            None when the SDK/config is unavailable.
        error: the exception that prevented client creation, if any.
    """

    def __init__(self, config=None):
        self.config = config or HindsightConfig()
        self.client = None
        self.error = None
        if self.config.enabled:
            try:
                from hindsight_client import Hindsight

                self.client = Hindsight(
                    base_url=self.config.api_url,
                    api_key=self.config.api_key or None,
                )
            except Exception as exc:  # noqa: BLE001 - degrade gracefully
                self.error = exc
                self.client = None

    # --- availability ------------------------------------------------------

    def available(self) -> bool:
        """True when the SDK is importable and the config is complete."""
        return self.client is not None

    def is_available(self) -> bool:  # alias kept for the old scaffold API
        return self.available()

    # --- lifecycle ---------------------------------------------------------

    def connect(self, ensure_bank=None) -> bool:
        """Make the wrapper ready to use. Optionally creates/updates the memory
        bank (best-effort, once per process) so its missions steer how Hindsight
        extracts and reflects. Never raises."""
        global _BANK_ENSURED
        if not self.available():
            return False
        if ensure_bank is None:
            ensure_bank = self.config.auto_create_bank
        if ensure_bank and not _BANK_ENSURED:
            _BANK_ENSURED = True
            try:
                self.client.create_bank(
                    bank_id=self.config.bank_id,
                    reflect_mission=self.config.reflect_mission,
                    retain_mission=self.config.retain_mission,
                )
            except Exception:  # noqa: BLE001 - bank may already exist / no perms
                pass
        return True

    def close(self) -> None:
        if self.client is not None:
            try:
                self.client.close()
            except Exception:  # noqa: BLE001
                pass
            self.client = None

    # --- memory operations -------------------------------------------------

    def retain(
        self,
        content: str,
        context: str | None = None,
        document_id: str | None = None,
        metadata: dict | None = None,
        tags: list | None = None,
        update_mode: str | None = None,
    ) -> dict | None:
        """Store a memory. Returns a small result dict, or None when
        unavailable/failed."""
        if not self.available():
            return None
        try:
            resp = self.client.retain(
                bank_id=self.config.bank_id,
                content=content,
                context=context,
                document_id=document_id,
                metadata=metadata,
                tags=tags,
                update_mode=update_mode,
            )
        except Exception:  # noqa: BLE001 - surface as None, caller handles it
            return None
        if resp is None:
            return None
        return {
            "ok": bool(getattr(resp, "success", True)),
            "items_count": getattr(resp, "items_count", 0),
            "document_id": document_id,
        }

    def recall(self, query: str, top_k: int = 5, budget: str = "mid",
               tags: list | None = None) -> list:
        """Recall memories matching the query. Returns the raw result items
        (objects with .id/.text/.metadata/...), or [] on failure."""
        if not self.available():
            return []
        try:
            resp = self.client.recall(
                bank_id=self.config.bank_id,
                query=query,
                budget=budget,
                # recall is token-budgeted, not count-budgeted; size it by top_k
                max_tokens=max(1024, top_k * 900),
                tags=tags,
            )
        except Exception:  # noqa: BLE001
            return []
        return list(getattr(resp, "results", None) or [])

    def reflect(self, query_or_ids, context: str | None = None) -> dict | None:
        """Synthesize an answer over the bank's memories. Accepts a query
        string, or a list of memory ids (which is turned into a query). Returns
        {'ok': True, 'insights': ..., 'based_on': [...]}, or None on failure."""
        if not self.available():
            return None
        if isinstance(query_or_ids, (list, tuple)):
            query = (
                "Synthesize the lessons from these past incident memories: "
                + ", ".join(str(i) for i in query_or_ids)
            )
        else:
            query = query_or_ids
        try:
            resp = self.client.reflect(
                bank_id=self.config.bank_id,
                query=query,
                context=context,
                budget="low",
                include_facts=True,
            )
        except Exception:  # noqa: BLE001
            return None
        if resp is None:
            return None
        facts = []
        based_on = getattr(resp, "based_on", None)
        if based_on is not None:
            for m in getattr(based_on, "memories", None) or []:
                t = getattr(m, "text", None)
                if t:
                    facts.append(t)
        insights = getattr(resp, "text", "") or ""
        if facts:
            insights += "\n\nCited memories:\n- " + "\n- ".join(facts)
        return {
            "ok": True,
            "insights": insights,
            "based_on": facts,
        }
