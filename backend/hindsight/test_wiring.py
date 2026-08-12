"""Tests for the Hindsight wiring, using a faked SDK — no network calls.

Run from the project root with the venv python:
    .venv/Scripts/python.exe backend/hindsight/test_wiring.py
"""
import os
import sys
import types
import unittest

# Make the project root importable regardless of how the test is invoked.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# --- Fake SDK ---------------------------------------------------------------


class FakeRetainResponse:
    def __init__(self, success=True):
        self.success = success
        self.items_count = 1


class FakeRecallResult:
    def __init__(self, rid, text, metadata=None, doc_id=None, score=None):
        self.id = rid
        self.text = text
        self.type = "experience"
        self.metadata = metadata or {}
        self.document_id = doc_id
        self.scores = (
            types.SimpleNamespace(final=score) if score is not None else None
        )


class FakeRecallResponse:
    def __init__(self, results):
        self.results = results


class FakeMemoryCite:
    def __init__(self, text):
        self.text = text


class FakeBasedOn:
    def __init__(self, memories):
        self.memories = memories


class FakeReflectResponse:
    def __init__(self, text, based_on=None):
        self.text = text
        self.based_on = based_on


class FakeHindsight:
    """Mimics the hindsight_client.Hindsight SDK surface we use."""

    def __init__(self, base_url=None, api_key=None, timeout=300.0,
                 user_agent=None, **kw):
        self.base_url = base_url
        self.api_key = api_key
        self.retain_calls = []
        self.recall_queries = []
        self.reflect_queries = []
        self.bank_creates = []

    def create_bank(self, bank_id, **kw):
        self.bank_creates.append((bank_id, kw))

    def retain(self, bank_id, content, **kw):
        self.retain_calls.append({"bank_id": bank_id, "content": content, **kw})
        return FakeRetainResponse(success=getattr(self, "retain_ok", True))

    def recall(self, bank_id, query, **kw):
        self.recall_queries.append({"bank_id": bank_id, "query": query, **kw})
        return FakeRecallResponse(
            [
                FakeRecallResult(
                    "mem-1",
                    "Incident: DB connection exhaustion\nResolution: bumped pool to 100",
                    {
                        "incident_id": "7",
                        "title": "Database connection exhaustion",
                        "service": "database",
                        "severity": "high",
                        "outcome": "resolved",
                        "root_cause": "connection leak",
                        "resolution": "bumped pool to 100",
                        "lesson": "watch pool utilization",
                    },
                    doc_id="incident-7",
                    score=0.91,
                ),
                FakeRecallResult(
                    "mem-2",
                    "Incident: Checkout 504s",
                    {"incident_id": "8", "service": "checkout", "outcome": "resolved"},
                    doc_id="incident-8",
                    score=0.72,
                ),
            ]
        )

    def reflect(self, bank_id, query, **kw):
        self.reflect_queries.append({"bank_id": bank_id, "query": query, **kw})
        return FakeReflectResponse(
            "**Insights:** past DB incidents point to connection-pool exhaustion.",
            based_on=FakeBasedOn(
                [FakeMemoryCite("Incident 7: bumped the connection pool")]
            ),
        )

    def close(self):
        pass


def install_fake_sdk():
    mod = types.ModuleType("hindsight_client")
    mod.Hindsight = FakeHindsight
    sys.modules["hindsight_client"] = mod


install_fake_sdk()

from backend.hindsight import client as hclient  # noqa: E402
from backend.hindsight.client import (  # noqa: E402
    HindsightConfig,
    HindsightClientWrapper,
)
from backend.hindsight.recall import recall_memories  # noqa: E402
from backend.hindsight.reflect import reflect_memories  # noqa: E402
from backend.hindsight.retain import (  # noqa: E402
    build_memory_text,
    build_metadata,
    retain_experience,
)
from backend.hindsight.schemas import IncidentExperience  # noqa: E402

ENV = {
    "HINDSIGHT_API_URL": "https://env.example",
    "HINDSIGHT_API_KEY": "env-key",
    "HINDSIGHT_BANK_ID": "env-bank",
}


class TestConfig(unittest.TestCase):
    def setUp(self):
        for k, v in ENV.items():
            os.environ[k] = v

    def tearDown(self):
        for k in ENV:
            os.environ.pop(k, None)

    def test_kwargs_override_env(self):
        cfg = HindsightConfig(api_url="https://kw.example", bank_id="kw-bank")
        self.assertEqual(cfg.api_url, "https://kw.example")
        self.assertEqual(cfg.bank_id, "kw-bank")
        self.assertEqual(cfg.api_key, "env-key")  # falls back to env
        self.assertTrue(cfg.enabled)

    def test_env_fallback(self):
        cfg = HindsightConfig()
        self.assertEqual(cfg.api_url, "https://env.example")
        self.assertEqual(cfg.api_key, "env-key")
        self.assertTrue(cfg.enabled)

    def test_disabled_without_url_or_bank(self):
        os.environ.pop("HINDSIGHT_API_URL")
        self.assertFalse(HindsightConfig().enabled)
        os.environ["HINDSIGHT_API_URL"] = "https://x.example"
        os.environ.pop("HINDSIGHT_BANK_ID")
        self.assertFalse(HindsightConfig().enabled)


class TestWrapper(unittest.TestCase):
    def setUp(self):
        for k, v in ENV.items():
            os.environ[k] = v
        hclient._BANK_ENSURED = False

    def tearDown(self):
        for k in ENV:
            os.environ.pop(k, None)

    def test_available_and_bank_creation_once(self):
        w = HindsightClientWrapper(HindsightConfig())
        self.assertTrue(w.available())
        self.assertTrue(w.is_available())
        w.connect()
        w.connect()
        self.assertEqual(len(w.client.bank_creates), 1, "bank created once")
        bank_id, kw = w.client.bank_creates[0]
        self.assertEqual(bank_id, "env-bank")
        self.assertIn("reflect_mission", kw)

    def test_bank_creation_once_across_instances(self):
        # connect() is called per request with a fresh wrapper; the bank must
        # only be created once per process, not once per request.
        w1 = HindsightClientWrapper(HindsightConfig())
        w2 = HindsightClientWrapper(HindsightConfig())
        self.assertTrue(w1.connect())
        self.assertTrue(w2.connect())
        self.assertEqual(len(w1.client.bank_creates), 1)
        self.assertEqual(len(w2.client.bank_creates), 0)

    def test_unavailable_when_disabled(self):
        os.environ["HINDSIGHT_API_URL"] = ""
        os.environ["HINDSIGHT_BANK_ID"] = ""
        w = HindsightClientWrapper(HindsightConfig())
        self.assertFalse(w.available())
        self.assertFalse(w.connect())
        self.assertIsNone(w.retain(content="x"))
        self.assertEqual(w.recall("q"), [])
        self.assertIsNone(w.reflect("q"))

    def test_close(self):
        w = HindsightClientWrapper(HindsightConfig())
        w.close()
        self.assertFalse(w.available())


class TestRetain(unittest.TestCase):
    def setUp(self):
        for k, v in ENV.items():
            os.environ[k] = v
        self.w = HindsightClientWrapper(HindsightConfig())

    def tearDown(self):
        for k in ENV:
            os.environ.pop(k, None)

    def _exp(self):
        return IncidentExperience(
            incident_id="42",
            title="DB connection exhaustion",
            service="database",
            severity="high",
            status="resolved",
            description="Connections exhausted under load",
            root_cause="connection leak in auth service",
            resolution="patched the connection pool",
            outcome="resolved",
            lesson="watch pool utilization",
        )

    def test_memory_text_contains_details(self):
        t = build_memory_text(self._exp())
        self.assertIn("Root cause: connection leak", t)
        self.assertIn("Resolution: patched the connection pool", t)
        self.assertIn("Lesson: watch pool utilization", t)

    def test_metadata(self):
        m = build_metadata(self._exp())
        self.assertEqual(m["incident_id"], "42")
        self.assertEqual(m["service"], "database")
        self.assertEqual(m["severity"], "high")
        self.assertEqual(m["outcome"], "resolved")

    def test_retain_with_dedup(self):
        res = retain_experience(self.w, self._exp())
        self.assertTrue(res["retained"])
        call = self.w.client.retain_calls[0]
        self.assertEqual(call["document_id"], "incident-42")
        self.assertEqual(call["update_mode"], "replace")
        self.assertIn("incident", call["tags"])
        self.assertIn("service:database", call["tags"])
        self.assertEqual(call["metadata"]["incident_id"], "42")
        self.assertIn("Resolution: patched the connection pool", call["content"])

    def test_retain_without_dedup(self):
        retain_experience(self.w, self._exp(), dedup=False)
        call = self.w.client.retain_calls[0]
        self.assertIsNone(call["update_mode"])

    def test_retain_unavailable(self):
        res = retain_experience(None, self._exp())
        self.assertFalse(res["retained"])

    def test_retain_reports_failure_when_sdk_fails(self):
        self.w.client.retain_ok = False
        res = retain_experience(self.w, self._exp())
        self.assertFalse(res["retained"])


class TestRecall(unittest.TestCase):
    def setUp(self):
        for k, v in ENV.items():
            os.environ[k] = v
        self.w = HindsightClientWrapper(HindsightConfig())

    def tearDown(self):
        for k in ENV:
            os.environ.pop(k, None)

    def test_recall_memories_mapping(self):
        mems = recall_memories(self.w, "db connections exhausted", top_k=5)
        self.assertEqual(len(mems), 2)
        m = mems[0]
        # keys the LLM prompt builder reads (suggest_fix.build_user_prompt)
        self.assertEqual(m["incident_id"], "7")
        self.assertEqual(m["service"], "database")
        self.assertEqual(m["severity"], "high")
        self.assertEqual(m["outcome"], "resolved")
        self.assertEqual(m["root_cause"], "connection leak")
        self.assertEqual(m["resolution"], "bumped pool to 100")
        self.assertEqual(m["lesson"], "watch pool utilization")
        self.assertEqual(m["score"], 0.91)
        self.assertIn("DB connection exhaustion", m["description"])
        # incident_id falls back to document_id when metadata lacks it
        self.assertEqual(mems[1]["incident_id"], "8")

    def test_recall_unavailable(self):
        os.environ["HINDSIGHT_API_URL"] = ""
        os.environ["HINDSIGHT_BANK_ID"] = ""
        w = HindsightClientWrapper(HindsightConfig())
        self.assertEqual(recall_memories(w, "anything"), [])
        self.assertEqual(recall_memories(None, "anything"), [])


class TestReflect(unittest.TestCase):
    def setUp(self):
        for k, v in ENV.items():
            os.environ[k] = v
        self.w = HindsightClientWrapper(HindsightConfig())

    def tearDown(self):
        for k in ENV:
            os.environ.pop(k, None)

    def test_reflect_with_query(self):
        res = reflect_memories(self.w, "database is slow")
        self.assertTrue(res["ok"])
        self.assertIn("connection-pool", res["insights"])
        self.assertIn("Cited memories", res["insights"])  # facts appended
        self.assertIn("bumped the connection pool", res["insights"])
        self.assertEqual(len(res["based_on"]), 1)
        self.assertEqual(self.w.client.reflect_queries[0]["query"], "database is slow")

    def test_reflect_with_id_list(self):
        res = self.w.reflect(["incident-7", "incident-8"])
        self.assertTrue(res["ok"])
        self.assertIn("incident-7", self.w.client.reflect_queries[0]["query"])

    def test_reflect_unavailable(self):
        os.environ["HINDSIGHT_API_URL"] = ""
        os.environ["HINDSIGHT_BANK_ID"] = ""
        w = HindsightClientWrapper(HindsightConfig())
        self.assertIsNone(reflect_memories(w, "x"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
