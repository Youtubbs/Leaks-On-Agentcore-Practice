# Findings

Scenario: a vet clinic booking agent. get_booking reads a booking record.
send_reminder sends an SMS reminder through a third-party partner.

| Leak | Where the data crossed | Where I closed it | What it still misses |
|---|---|---|---|
| OUT | send_reminder passes booking data to the SMS partner. | for_partner in controls.py keeps only sms_to, slot and clinic (an allow-list), then checks the result with ApplyGuardrail and refuses to send if it intervenes. | The phone number still goes out, because the partner needs it to send the SMS. A token from the partner instead of the real number would fix that. |
| IN | get_booking returns the notes field, which contains a card number staff typed in. The model sees it. | (not closed) | Closing it means masking notes before the model sees them. That costs a Comprehend call on every read, and if Comprehend is down the whole note is withheld, so the agent also loses useful info like "nervous around dogs". The real fix is a separate payment field so card numbers never go in notes. |
| STORED | Every tool call writes a line to audit.json. | write_record in store.py runs every record through for_storage (Comprehend detect_pii_entities) before writing, and only writes the masked version. | Comprehend is a model, so it can miss things like unusual name spellings, odd card formats, and UK-only identifiers like a National Insurance number, which it may have no entity type for (I didn't look). The log file itself is also not encrypted. |

## Why each API is where it is

- for_partner uses ApplyGuardrail (a decision API) because outbound we can just refuse to send, and a missed reminder is better than a leak.
- for_storage uses Comprehend detect_pii_entities (a transformation API) because we still have to write the audit record, so masking is more useful than a yes/no answer.

## Fail open or fail closed?

Both controls fail closed, on purpose. If the guardrail is unavailable or not configured, for_partner raises an error and nothing is sent. If Comprehend is unavailable, each text field is written as [WITHHELD] instead of the raw value. This means an outage loses some log detail and stops reminders, but it never writes or sends raw personal data, which is the outcome I care about more.

## What I would do with another day

Split the notes field so payment details have their own field and never land in free text, which would close the IN leak properly. Send the partner a token instead of the real phone number. Add a check for UK identifiers that doesn't rely on Comprehend. Run the tests against the real AWS services.
