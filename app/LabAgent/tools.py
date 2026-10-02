from .controls import for_partner
from .store import write_record

# Fake backing store
BOOKINGS = {
    "VET-1001": {
        "booking_ref": "VET-1001",
        "owner_name": "Reginold Thistlewick Cumberbatch",
        "pet_name": "Biscuit",
        "email": "marigold@example.test",
        "phone": "+44 7700 900412",
        "address": "14 Gurnard Lane, Fakehampton",
        "slot": "2026-10-09 09:30",
        # IN leak where staff typed a card number into a free-text field.
        "notes": "Paid deposit with card 4111 1111 1111 1111. Biscuit is nervous around dogs. ",
    }
}

SENT_TO_PARTNER = []


def get_booking(booking_ref: str) -> dict:
    """Look up a vet clinic booking by its booking reference."""
    record = BOOKINGS.get(booking_ref)
    if record is None:
        return {"error": "booking not found"}
    write_record("booking_read", record)
    return record


def send_reminder(booking_ref: str) -> dict:
    """Send the customer an SMS reminder for their booking through the partner service."""
    record = BOOKINGS.get(booking_ref)
    if record is None:
        return {"error": "booking not found"}
    message = dict(record, sms_to=record["phone"], clinic="Fakehampton Vets")
    try:
        payload = for_partner(message)
    except ValueError:
        write_record("reminder_blocked", {"booking_ref": booking_ref})
        return {"sent": False}
    SENT_TO_PARTNER.append(payload)
    write_record("reminder_sent", payload)
    return {"sent": True}
