"""Data schemas for the Hindsight integration."""
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class IncidentExperience:
    """A resolved incident shaped as an experience to retain in Hindsight.

    Field names match what the rest of the app (app.py) constructs, and the
    values are mapped onto Hindsight memory content + metadata on retain.
    """

    incident_id: Optional[str] = None
    title: Optional[str] = None
    service: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    outcome: Optional[str] = None
    lesson: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to a plain dict (None values included)."""
        return asdict(self)
