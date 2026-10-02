import json
import os

from .controls import for_storage

LOG_FILE = os.environ.get("AUDIT_LOG", "audit.jsonl")


def write_record(event, record):
    # Redact at the moment of writing, not as a pass later.
    line = json.dumps({"event": event, **for_storage(record)})
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
