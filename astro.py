"""Core astrology data and helpers. Pure Python, no Flask, so it is easy to test."""
import re
from datetime import date

# The text-presentation selector (U+FE0E) stops phones turning symbols into emoji.
TEXT = "\ufe0e"

SIGNS = [
    {"name": "Aries", "element": "fire", "modality": "cardinal", "glyph": "\u2648" + TEXT},
    {"name": "Taurus", "element": "earth", "modality": "fixed", "glyph": "\u2649" + TEXT},
    {"name": "Gemini", "element": "air", "modality": "mutable", "glyph": "\u264A" + TEXT},
    {"name": "Cancer", "element": "water", "modality": "cardinal", "glyph": "\u264B" + TEXT},
    {"name": "Leo", "element": "fire", "modality": "fixed", "glyph": "\u264C" + TEXT},
    {"name": "Virgo", "element": "earth", "modality": "mutable", "glyph": "\u264D" + TEXT},
    {"name": "Libra", "element": "air", "modality": "cardinal", "glyph": "\u264E" + TEXT},
    {"name": "Scorpio", "element": "water", "modality": "fixed", "glyph": "\u264F" + TEXT},
    {"name": "Sagittarius", "element": "fire", "modality": "mutable", "glyph": "\u2650" + TEXT},
    {"name": "Capricorn", "element": "earth", "modality": "cardinal", "glyph": "\u2651" + TEXT},
    {"name": "Aquarius", "element": "air", "modality": "fixed", "glyph": "\u2652" + TEXT},
    {"name": "Pisces", "element": "water", "modality": "mutable", "glyph": "\u2653" + TEXT},
]

SIGN_NAMES = [s["name"] for s in SIGNS]

# required: the wheel cannot be drawn without these.
# can_retrograde: whether the retrograde checkbox makes sense for the body.
BODIES = [
    {"name": "Sun", "glyph": "\u2609" + TEXT, "required": True, "can_retrograde": False},
    {"name": "Moon", "glyph": "\u263D" + TEXT, "required": True, "can_retrograde": False},
    {"name": "Ascendant", "glyph": "AC", "required": True, "can_retrograde": False},
    {"name": "Mercury", "glyph": "\u263F" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Venus", "glyph": "\u2640" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Mars", "glyph": "\u2642" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Jupiter", "glyph": "\u2643" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Saturn", "glyph": "\u2644" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Uranus", "glyph": "\u2645" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Neptune", "glyph": "\u2646" + TEXT, "required": False, "can_retrograde": True},
    {"name": "Pluto", "glyph": "\u2647" + TEXT, "required": False, "can_retrograde": True},
    {"name": "North Node", "glyph": "\u260A" + TEXT, "required": False, "can_retrograde": False},
]

BODY_BY_NAME = {b["name"]: b for b in BODIES}

# A fictional chart so the app can be explored before you enter your own.
SAMPLE_PLACEMENTS = [
    {"body": "Sun", "sign": "Leo", "degree": 14, "minute": 32, "retrograde": 0},
    {"body": "Moon", "sign": "Pisces", "degree": 3, "minute": 10, "retrograde": 0},
    {"body": "Ascendant", "sign": "Scorpio", "degree": 22, "minute": 5, "retrograde": 0},
    {"body": "Mercury", "sign": "Virgo", "degree": 2, "minute": 48, "retrograde": 0},
    {"body": "Venus", "sign": "Cancer", "degree": 27, "minute": 15, "retrograde": 0},
    {"body": "Mars", "sign": "Gemini", "degree": 9, "minute": 40, "retrograde": 0},
    {"body": "Jupiter", "sign": "Libra", "degree": 18, "minute": 2, "retrograde": 0},
    {"body": "Saturn", "sign": "Aquarius", "degree": 25, "minute": 50, "retrograde": 1},
    {"body": "Uranus", "sign": "Taurus", "degree": 6, "minute": 12, "retrograde": 0},
    {"body": "Neptune", "sign": "Pisces", "degree": 1, "minute": 7, "retrograde": 0},
    {"body": "Pluto", "sign": "Capricorn", "degree": 29, "minute": 30, "retrograde": 0},
    {"body": "North Node", "sign": "Aries", "degree": 11, "minute": 0, "retrograde": 0},
]


def sign_index(sign):
    """Position of a sign in the zodiac, Aries = 0 ... Pisces = 11."""
    return SIGN_NAMES.index(sign)


def to_longitude(sign, degree, minute=0):
    """Ecliptic longitude in degrees (0 to 360). Aries 0 degrees is 0."""
    return sign_index(sign) * 30 + degree + minute / 60


def house_for(longitude, asc_longitude):
    """Whole-sign house (1 to 12): the Ascendant's sign is the 1st house."""
    return (int(longitude // 30) - int(asc_longitude // 30)) % 12 + 1


def format_position(degree, minute):
    return f"{degree}\u00b0{minute:02d}\u2032"


def wheel_data(placements):
    """Turn stored placements into the structure used by both the page and the wheel."""
    by_body = {p["body"]: p for p in placements}
    if "Ascendant" not in by_body:
        raise ValueError("A chart needs an Ascendant to place the houses.")

    asc = by_body["Ascendant"]
    asc_longitude = to_longitude(asc["sign"], asc["degree"], asc["minute"])

    rows = []
    for body in BODIES:
        p = by_body.get(body["name"])
        if p is None:
            continue
        longitude = to_longitude(p["sign"], p["degree"], p["minute"])
        rows.append(
            {
                "body": body["name"],
                "glyph": body["glyph"],
                "sign": p["sign"],
                "signGlyph": SIGNS[sign_index(p["sign"])]["glyph"],
                "degree": p["degree"],
                "minute": p["minute"],
                "position": format_position(p["degree"], p["minute"]),
                "longitude": round(longitude, 4),
                "house": house_for(longitude, asc_longitude),
                "retrograde": bool(p["retrograde"]),
            }
        )
    return {"ascSignIndex": int(asc_longitude // 30), "placements": rows}


def parse_placements(form):
    """Read and validate the placement fields of the new-chart form.

    Returns (placements, errors). Blank optional bodies are skipped.
    """
    placements, errors = [], []
    for body in BODIES:
        name = body["name"]
        sign = form.get(f"sign_{name}", "").strip()
        degree_raw = form.get(f"deg_{name}", "").strip()
        minute_raw = form.get(f"min_{name}", "").strip()

        if not sign and not degree_raw and not minute_raw:
            if body["required"]:
                errors.append(f"{name} is required.")
            continue

        if sign not in SIGN_NAMES:
            errors.append(f"Choose a sign for {name}.")
            continue
        try:
            degree = int(degree_raw)
            minute = int(minute_raw) if minute_raw else 0
        except ValueError:
            errors.append(f"{name}: degree and minute must be whole numbers.")
            continue
        if not 0 <= degree <= 29:
            errors.append(f"{name}: degree must be between 0 and 29.")
            continue
        if not 0 <= minute <= 59:
            errors.append(f"{name}: minute must be between 0 and 59.")
            continue

        retrograde = 1 if body["can_retrograde"] and form.get(f"rx_{name}") else 0
        placements.append(
            {"body": name, "sign": sign, "degree": degree, "minute": minute, "retrograde": retrograde}
        )
    return placements, errors


def parse_birth_details(form):
    """Validate the optional birth date, time and place. Returns (details, errors)."""
    errors = []
    birth_date = form.get("birth_date", "").strip()
    birth_time = form.get("birth_time", "").strip()
    birth_place = form.get("birth_place", "").strip()

    if birth_date:
        try:
            date.fromisoformat(birth_date)
        except ValueError:
            errors.append("Birth date must look like 1999-08-14.")
    if birth_time and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", birth_time):
        errors.append("Birth time must look like 06:45 (24-hour).")
    if len(birth_place) > 120:
        errors.append("Birth place is too long (120 characters maximum).")

    details = {
        "birth_date": birth_date or None,
        "birth_time": birth_time or None,
        "birth_place": birth_place or None,
    }
    return details, errors
