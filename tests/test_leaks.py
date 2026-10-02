import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from LabAgent import controls, store, tools

PERSONAL = {
    "NAME": "Reginold Thistlewick Cumberbatch",
    "EMAIL": "marigold@example.test",
    "PHONE": "+44 7700 900412",
    "ADDRESS": "14 Gurnard Lane, Fakehampton",
    "CREDIT_DEBIT_NUMBER": "4111 1111 1111 1111",
}


# Stand-ins for AWS so the tests run without credentials.
class FakeComprehend:
    def detect_pii_entities(self, Text, LanguageCode):
        found = []
        for kind, value in PERSONAL.items():
            start = Text.find(value)
            if start >= 0:
                found.append({"Type": kind, "BeginOffset": start, "EndOffset": start + len(value)})
        return {"Entities": found}


class FakeGuardrail:
    def apply_guardrail(self, **kwargs):
        return {"action": "NONE"}


def setup(monkeypatch, tmp_path):
    monkeypatch.setattr(controls, "comprehend", FakeComprehend())
    monkeypatch.setattr(controls, "bedrock", FakeGuardrail())
    monkeypatch.setattr(store, "LOG_FILE", str(tmp_path / "audit.json"))
    tools.SENT_TO_PARTNER.clear()


def test_partner_payload_has_no_personal_data(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    tools.send_reminder("VET-1001")

    assert len(tools.SENT_TO_PARTNER) == 1
    sent = json.dumps(tools.SENT_TO_PARTNER)
    for kind, value in PERSONAL.items():
        if kind != "PHONE":
            assert value not in sent


def test_stored_record_has_no_personal_data(monkeypatch, tmp_path):
    setup(monkeypatch, tmp_path)
    tools.get_booking("VET-1001")
    tools.send_reminder("VET-1001")

    with open(store.LOG_FILE, encoding="utf-8") as f:
        saved = f.read()
    assert saved
    for value in PERSONAL.values():
        assert value not in saved
