"""Validation for journal notes."""
from datetime import date

from . import astro

MAX_NOTE_LENGTH = 2000


def parse_note(form):
    """Read and validate a note form. Returns (data, errors)."""
    errors = []
    content = form.get("content", "").strip()
    body = form.get("body", "").strip()
    entry_date = form.get("entry_date", "").strip() or date.today().isoformat()

    if not content:
        errors.append("Write something before saving the note.")
    elif len(content) > MAX_NOTE_LENGTH:
        errors.append(f"A note can be at most {MAX_NOTE_LENGTH} characters.")

    if body and body not in astro.BODY_BY_NAME:
        errors.append("Choose a valid placement, or leave it as the whole chart.")

    try:
        date.fromisoformat(entry_date)
    except ValueError:
        errors.append("The date must look like 2026-10-12.")

    return {"content": content, "body": body or None, "entry_date": entry_date}, errors
