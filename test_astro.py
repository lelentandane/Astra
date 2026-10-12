import pytest

from astra import astro


def test_longitude_uses_sign_degree_and_minute():
    assert astro.to_longitude("Aries", 0) == 0
    assert astro.to_longitude("Taurus", 0) == 30
    assert astro.to_longitude("Pisces", 29, 30) == pytest.approx(359.5)


def test_whole_sign_houses_start_at_the_ascendant_sign():
    asc = astro.to_longitude("Scorpio", 22, 5)
    assert astro.house_for(astro.to_longitude("Scorpio", 1), asc) == 1
    assert astro.house_for(astro.to_longitude("Sagittarius", 10), asc) == 2
    assert astro.house_for(astro.to_longitude("Leo", 14), asc) == 10
    assert astro.house_for(astro.to_longitude("Libra", 29), asc) == 12


def test_houses_wrap_around_the_zodiac():
    asc = astro.to_longitude("Pisces", 5)
    assert astro.house_for(astro.to_longitude("Aries", 1), asc) == 2
    assert astro.house_for(astro.to_longitude("Aquarius", 20), asc) == 12


def test_wheel_data_requires_an_ascendant():
    with pytest.raises(ValueError):
        astro.wheel_data([{"body": "Sun", "sign": "Leo", "degree": 1, "minute": 0, "retrograde": 0}])


def test_sample_chart_builds_a_wheel():
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    assert wheel["ascSignIndex"] == 7  # Scorpio
    sun = next(p for p in wheel["placements"] if p["body"] == "Sun")
    assert sun["house"] == 10
    assert sun["position"] == "14\u00b032\u2032"


def test_parse_placements_accepts_valid_input():
    from tests.conftest import valid_form

    placements, errors = astro.parse_placements(valid_form())
    assert errors == []
    assert [p["body"] for p in placements] == ["Sun", "Moon", "Ascendant"]


@pytest.mark.parametrize(
    "overrides, fragment",
    [
        ({"deg_Sun": "30"}, "between 0 and 29"),
        ({"min_Sun": "60"}, "between 0 and 59"),
        ({"deg_Sun": "abc"}, "whole numbers"),
        ({"sign_Sun": "Ophiuchus"}, "Choose a sign"),
        ({"sign_Moon": "", "deg_Moon": "", "min_Moon": ""}, "Moon is required"),
    ],
)
def test_parse_placements_rejects_bad_input(overrides, fragment):
    from tests.conftest import valid_form

    _, errors = astro.parse_placements(valid_form(**overrides))
    assert any(fragment in e for e in errors)


def test_retrograde_only_applies_to_bodies_that_can_have_it():
    from tests.conftest import valid_form

    form = valid_form(sign_Saturn="Aquarius", deg_Saturn="25", rx_Saturn="on", rx_Sun="on")
    placements, errors = astro.parse_placements(form)
    assert errors == []
    by_body = {p["body"]: p for p in placements}
    assert by_body["Saturn"]["retrograde"] == 1
    assert by_body["Sun"]["retrograde"] == 0


def test_birth_details_validation():
    _, errors = astro.parse_birth_details({"birth_date": "14-08-1999", "birth_time": "25:00"})
    assert len(errors) == 2
    details, errors = astro.parse_birth_details({"birth_date": "1999-08-14", "birth_time": "06:45"})
    assert errors == []
    assert details["birth_place"] is None


# ---------------------------------------------------------------- aspects

def test_angular_distance_takes_the_short_way_round():
    assert astro.angular_distance(10, 350) == 20
    assert astro.angular_distance(0, 180) == 180
    assert astro.angular_distance(90, 90) == 0


def test_find_aspects_detects_each_aspect_type():
    points = [("Sun", 0), ("Mercury", 3), ("Venus", 60), ("Mars", 92), ("Jupiter", 120), ("Saturn", 180)]
    found = {(a["a"], a["b"]): a["type"] for a in astro.find_aspects(points)}
    assert found[("Sun", "Mercury")] == "Conjunction"
    assert found[("Sun", "Venus")] == "Sextile"
    assert found[("Sun", "Mars")] == "Square"
    assert found[("Sun", "Jupiter")] == "Trine"
    assert found[("Sun", "Saturn")] == "Opposition"


def test_aspects_outside_orb_are_ignored():
    assert astro.find_aspects([("Sun", 0), ("Moon", 100)]) == []  # 10 degrees from a square, orb is 6
    assert astro.find_aspects([("Sun", 0), ("Moon", 66)]) == []  # 6 degrees from a sextile, orb is 4


def test_points_use_a_tighter_orb():
    # 5 degrees off a trine is fine between planets but too wide for the North Node.
    assert len(astro.find_aspects([("Sun", 0), ("Moon", 125)])) == 1
    assert astro.find_aspects([("Sun", 0), ("North Node", 125)]) == []


def test_aspects_are_sorted_by_tightest_orb():
    found = astro.find_aspects([("Sun", 0), ("Moon", 5), ("Mars", 1)])
    orbs = [a["orb"] for a in found]
    assert orbs == sorted(orbs)


def test_orb_text_is_in_degrees_and_minutes():
    assert astro.format_orb(1.5) == "1\u00b030\u2032"
    assert astro.format_orb(0.3667) == "0\u00b022\u2032"


def test_wheel_data_includes_aspects_for_the_sample_chart():
    wheel = astro.wheel_data(astro.SAMPLE_PLACEMENTS)
    pairs = {(a["a"], a["b"]): a["type"] for a in wheel["aspects"]}
    assert pairs[("Moon", "Mercury")] == "Opposition"


@pytest.mark.parametrize("number, expected", [(1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th"), (11, "11th"), (12, "12th"), (21, "21st")])
def test_ordinal(number, expected):
    assert astro.ordinal(number) == expected
