import pytest

from astra import journal, repository
from astra.db import get_db
from tests.conftest import valid_form


@pytest.fixture
def chart(client):
    client.post("/charts/new", data=valid_form())
    return 1


def test_parse_note_defaults_the_date_and_blank_body():
    data, errors = journal.parse_note({"content": "  Felt very seen today.  "})
    assert errors == []
    assert data["content"] == "Felt very seen today."
    assert data["body"] is None
    assert len(data["entry_date"]) == 10


@pytest.mark.parametrize(
    "form, fragment",
    [
        ({"content": "   "}, "Write something"),
        ({"content": "x" * 2001}, "at most"),
        ({"content": "ok", "body": "Chiron"}, "valid placement"),
        ({"content": "ok", "entry_date": "12/10/2026"}, "must look like"),
    ],
)
def test_parse_note_rejects_bad_input(form, fragment):
    _, errors = journal.parse_note(form)
    assert any(fragment in e for e in errors)


def test_add_edit_and_delete_a_note(client, app, chart):
    response = client.post(
        f"/charts/{chart}/notes",
        data={"content": "Venus week went well.", "body": "Venus", "entry_date": "2026-10-01", "return_to": "journal"},
        follow_redirects=True,
    )
    assert b"Note saved." in response.data
    assert b"Venus week went well." in response.data

    response = client.post(
        "/notes/1/edit",
        data={"content": "Updated thought.", "body": "", "entry_date": "2026-10-02"},
        follow_redirects=True,
    )
    assert b"Updated thought." in response.data
    assert b"Whole chart" in response.data

    response = client.post("/notes/1/delete", follow_redirects=True)
    assert b"Note deleted." in response.data
    assert b"Updated thought." not in response.data


def test_empty_note_is_rejected_with_a_message(client, chart):
    response = client.post(f"/charts/{chart}/notes", data={"content": "  ", "return_to": "journal"}, follow_redirects=True)
    assert b"Write something" in response.data


def test_notes_are_listed_newest_first_and_can_be_filtered(client, app, chart):
    with app.app_context():
        db = get_db()
        repository.add_note(db, chart, {"content": "older", "body": "Sun", "entry_date": "2026-01-01"})
        repository.add_note(db, chart, {"content": "newer", "body": "Moon", "entry_date": "2026-06-01"})
        repository.add_note(db, chart, {"content": "about 50% of it", "body": None, "entry_date": "2026-03-01"})

        assert [n["content"] for n in repository.list_notes(db, chart)] == ["newer", "about 50% of it", "older"]
        assert [n["content"] for n in repository.list_notes(db, chart, body="Sun")] == ["older"]
        assert [n["content"] for n in repository.list_notes(db, chart, body="")] == ["about 50% of it"]
        assert [n["content"] for n in repository.list_notes(db, chart, query="newer")] == ["newer"]
        # a literal percent sign must not act as a wildcard
        assert [n["content"] for n in repository.list_notes(db, chart, query="50%")] == ["about 50% of it"]
        assert repository.list_notes(db, chart, query="%") != repository.list_notes(db, chart)


def test_journal_filter_options(client, app, chart):
    with app.app_context():
        repository.add_note(get_db(), chart, {"content": "sun note", "body": "Sun", "entry_date": "2026-01-01"})
        repository.add_note(get_db(), chart, {"content": "chart note", "body": None, "entry_date": "2026-01-02"})
    assert b"sun note" in client.get(f"/charts/{chart}/journal?body=Sun").data
    assert b"chart note" not in client.get(f"/charts/{chart}/journal?body=Sun").data
    assert b"chart note" in client.get(f"/charts/{chart}/journal?body=chart").data
    assert b"sun note" not in client.get(f"/charts/{chart}/journal?body=chart").data
    assert b"2 of 2 notes" in client.get(f"/charts/{chart}/journal").data


def test_deleting_a_chart_deletes_its_notes(client, app, chart):
    client.post(f"/charts/{chart}/notes", data={"content": "gone soon", "return_to": "journal"})
    client.post(f"/charts/{chart}/delete")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0


def test_note_text_is_escaped_in_html(client, chart):
    client.post(f"/charts/{chart}/notes", data={"content": "<script>alert(1)</script>", "return_to": "journal"})
    page = client.get(f"/charts/{chart}/journal").data
    assert b"<script>alert(1)</script>" not in page
    assert b"&lt;script&gt;" in page


def test_unknown_note_is_a_404(client):
    assert client.get("/notes/99/edit").status_code == 404
    assert client.post("/notes/99/delete").status_code == 404
