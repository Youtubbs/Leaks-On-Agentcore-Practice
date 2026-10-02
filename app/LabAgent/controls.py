import json
import os

import boto3

GUARDRAIL_ID = os.environ.get("GUARDRAIL_ID", "")
GUARDRAIL_VERSION = os.environ.get("GUARDRAIL_VERSION", "DRAFT")
REGION = os.environ.get("AWS_REGION", "us-east-1")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)
comprehend = boto3.client("comprehend", region_name=REGION)

# Allow-list, not a deny-list. any field added to a record later is
# blocked by default instead of leaking until someone remembers to deny it.
PARTNER_FIELDS = ["sms_to", "slot", "clinic"]


def for_partner(record):
    # Decision API (ApplyGuardrail) is outbound we can simply refuse to send.
    payload = {key: record[key] for key in PARTNER_FIELDS if key in record}
    try:
        result = bedrock.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            source="OUTPUT",
            content=[{"text": {"text": json.dumps(payload)}}],
        )
        allowed = result["action"] == "NONE"
    except Exception:
        allowed = False
    if not allowed:
        raise ValueError("guardrail blocked the partner payload")
    return payload


def for_storage(record):
    # Transformation API (Comprehend) is we still have to write the record,
    # so we mask the personal data instead of refusing.
    return {key: mask(value) if isinstance(value, str) else value for key, value in record.items()}


def mask(text):
    try:
        entities = comprehend.detect_pii_entities(Text=text, LanguageCode="en")["Entities"]
    except Exception:
        return "[WITHHELD]"
    for entity in sorted(entities, key=lambda e: e["BeginOffset"], reverse=True):
        text = text[:entity["BeginOffset"]] + "[" + entity["Type"] + "]" + text[entity["EndOffset"]:]
    return text
