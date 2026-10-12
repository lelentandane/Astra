import pytest

from astra import astro, content, interpret, repository
from astra.db import get_db


@pytest.fixture
def interpretations(app):
    with app.app_context():
        return repository.get_interpretations(get_db())


def test_every_body_sign_house_and_aspect_has_content(interpretations):
    assert set(interpretations["body"]) == {b["name"] for b in astro.BODIES}
    assert set(interpretations["sign"]) == set(astro.SIGN_NAMES)
    assert set(interpretations["house"]) == {str(n) for n in range(1, 13)}
    assert set(interpretations["aspect"]) == {a["name"] for a in astro.ASPECTS}


def test_seeding_is_repeatable_and_does_not_duplicate(app):
    with app.app_context():
        db = get_db()
        before = db.execute("SELECT COUNT(*) FROM interpretations").fetchone()[0]
        repository.seed_interpretations(db)
        after = db.execute("SELECT COUNT(*) FROM interpretations").fetchone()[0]
    assert before == after == len(content.all_entries())


def test_topics_are_stored_in_their_own_table(interpretations):
    assert "Relationships" in interpretations["body"]["Venus"]["topics"]
    assert interpretations["sign"]["Leo"]["topics"] == []


def test_every_topic_used_in_content_is_declared():
    for entry in content.all_entries():
        for topic in entry["topics"]:
            assert topic in content.TOPICS


def test_reading_combines_body_sign_and_house(interpretations):
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    readings = interpret.build_readings(wheel, interpretations)
    sun = readings["Sun"]
    assert sun["title"] == "Sun in Leo, 10th house"
    assert [part["label"] for part in sun["parts"]] == ["Sun", "Leo", "10th house"]
    assert "Career" in sun["topics"]  # from the 10th house


def test_ascendant_reading_has_no_house_layer(interpretations):
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    asc = interpret.build_readings(wheel, interpretations)["Ascendant"]
    assert asc["title"] == "Ascendant in Scorpio"
    assert len(asc["parts"]) == 2


def test_aspect_text_names_both_bodies(interpretations):
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    moon = interpret.build_readings(wheel, interpretations)["Moon"]
    opposition = next(a for a in moon["aspects"] if a["label"] == "Opposition Mercury")
    assert "Moon" in opposition["text"] and "Mercury" in opposition["text"]


def test_topics_in_use_follow_the_standard_order(interpretations):
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    topics = interpret.topics_in_use(interpret.build_readings(wheel, interpretations))
    assert topics == [t for t in content.TOPICS if t in topics]
