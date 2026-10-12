import pytest

from astra import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def valid_form(**overrides):
    """Smallest valid form: name plus the three required placements."""
    data = {
        "name": "Test chart",
        "sign_Sun": "Leo", "deg_Sun": "14", "min_Sun": "32",
        "sign_Moon": "Pisces", "deg_Moon": "3", "min_Moon": "10",
        "sign_Ascendant": "Scorpio", "deg_Ascendant": "22", "min_Ascendant": "5",
    }
    data.update(overrides)
    return data
