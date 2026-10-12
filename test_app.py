from tests.conftest import valid_form


def test_home_shows_welcome_when_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Create your chart" in response.data


def test_create_view_and_delete_a_chart(client):
    response = client.post("/charts/new", data=valid_form(), follow_redirects=True)
    assert response.status_code == 200
    assert b"Test chart" in response.data
    assert b"10th" in response.data  # Leo is the 10th house for Scorpio rising

    home = client.get("/")
    assert b"Sun in Leo" in home.data

    response = client.post("/charts/1/delete", follow_redirects=True)
    assert b"Chart deleted." in response.data
    assert client.get("/charts/1").status_code == 404


def test_invalid_form_shows_errors_and_keeps_input(client):
    response = client.post("/charts/new", data=valid_form(deg_Sun="45"))
    assert response.status_code == 400
    assert b"between 0 and 29" in response.data
    assert b'value="Test chart"' in response.data


def test_sample_chart_loads_once(client):
    first = client.post("/charts/sample", follow_redirects=True)
    assert b"Sample chart (fictional)" in first.data
    second = client.post("/charts/sample", follow_redirects=True)
    assert b"already loaded" in second.data


def test_missing_chart_is_a_404(client):
    response = client.get("/charts/999")
    assert response.status_code == 404
    assert b"does not exist" in response.data
