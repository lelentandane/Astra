"""Builds readings from stored interpretation pieces.

A reading for a placement is assembled from three layers:
the body (what), the sign (how) and the house (where),
plus a sentence for each aspect that touches the body.
No AI and no network calls: it is a small rule-based engine.
"""
from . import astro, content


def build_readings(wheel, interpretations):
    """Return {body_name: reading} for every placement in the wheel data."""
    bodies = interpretations["body"]
    signs = interpretations["sign"]
    houses = interpretations["house"]
    aspect_texts = interpretations["aspect"]

    readings = {}
    for placement in wheel["placements"]:
        name = placement["body"]
        body = bodies[name]
        sign = signs[placement["sign"]]

        parts = [
            {"label": name, "keyword": body["keyword"], "text": body["text"]},
            {"label": placement["sign"], "keyword": sign["keyword"], "text": sign["text"]},
        ]
        topics = set(body["topics"])

        # The Ascendant is the 1st house cusp by definition, so a house layer adds nothing.
        if name == "Ascendant":
            title = f"{name} in {placement['sign']}"
        else:
            house = houses[str(placement["house"])]
            label = f"{astro.ordinal(placement['house'])} house"
            parts.append({"label": label, "keyword": house["keyword"], "text": house["text"]})
            topics |= set(house["topics"])
            title = f"{name} in {placement['sign']}, {label}"

        aspects = []
        for aspect in wheel["aspects"]:
            if name not in (aspect["a"], aspect["b"]):
                continue
            other = aspect["b"] if aspect["a"] == name else aspect["a"]
            template = aspect_texts[aspect["type"]]
            aspects.append(
                {
                    "label": f"{aspect['type']} {other}",
                    "orbText": aspect["orbText"],
                    "nature": aspect["nature"],
                    "keyword": template["keyword"],
                    "text": template["text"].format(a=aspect["a"], b=aspect["b"]),
                }
            )

        readings[name] = {
            "title": title,
            "parts": parts,
            "aspects": aspects,
            "topics": sorted(topics, key=content.TOPICS.index),
        }
    return readings


def topics_in_use(readings):
    """Topics that appear in at least one reading, in the standard order."""
    used = {topic for reading in readings.values() for topic in reading["topics"]}
    return [topic for topic in content.TOPICS if topic in used]
