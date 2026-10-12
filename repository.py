"""All SQL lives here, so routes stay short and readable."""


def create_chart(db, name, details, placements, is_sample=False):
    cursor = db.execute(
        "INSERT INTO charts (name, birth_date, birth_time, birth_place, is_sample) "
        "VALUES (?, ?, ?, ?, ?)",
        (name, details.get("birth_date"), details.get("birth_time"), details.get("birth_place"), int(is_sample)),
    )
    chart_id = cursor.lastrowid
    db.executemany(
        "INSERT INTO placements (chart_id, body, sign, degree, minute, retrograde) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(chart_id, p["body"], p["sign"], p["degree"], p["minute"], p["retrograde"]) for p in placements],
    )
    db.commit()
    return chart_id


def list_charts(db):
    """Every chart with its Sun, Moon and Ascendant signs for the home page."""
    charts = db.execute(
        "SELECT * FROM charts ORDER BY is_sample ASC, created_at DESC, id DESC"
    ).fetchall()
    summaries = []
    for chart in charts:
        rows = db.execute(
            "SELECT body, sign FROM placements "
            "WHERE chart_id = ? AND body IN ('Sun', 'Moon', 'Ascendant')",
            (chart["id"],),
        ).fetchall()
        signs = {row["body"]: row["sign"] for row in rows}
        summaries.append({"chart": chart, "signs": signs})
    return summaries


def get_chart(db, chart_id):
    return db.execute("SELECT * FROM charts WHERE id = ?", (chart_id,)).fetchone()


def get_placements(db, chart_id):
    return db.execute("SELECT * FROM placements WHERE chart_id = ?", (chart_id,)).fetchall()


def has_sample(db):
    return db.execute("SELECT 1 FROM charts WHERE is_sample = 1").fetchone() is not None


def delete_chart(db, chart_id):
    db.execute("DELETE FROM charts WHERE id = ?", (chart_id,))
    db.commit()


# ---------------------------------------------------------------- interpretations

def seed_interpretations(db):
    """Insert or refresh the interpretation pieces from content.py."""
    from . import content

    for entry in content.all_entries():
        db.execute(
            "INSERT INTO interpretations (kind, key, keyword, text) VALUES (?, ?, ?, ?) "
            "ON CONFLICT (kind, key) DO UPDATE SET keyword = excluded.keyword, text = excluded.text",
            (entry["kind"], entry["key"], entry["keyword"], entry["text"]),
        )
        row = db.execute(
            "SELECT id FROM interpretations WHERE kind = ? AND key = ?", (entry["kind"], entry["key"])
        ).fetchone()
        db.execute("DELETE FROM interpretation_topics WHERE interpretation_id = ?", (row["id"],))
        db.executemany(
            "INSERT INTO interpretation_topics (interpretation_id, topic) VALUES (?, ?)",
            [(row["id"], topic) for topic in entry["topics"]],
        )
    db.commit()


def get_interpretations(db):
    """Return {kind: {key: {keyword, text, topics}}}."""
    result = {"body": {}, "sign": {}, "house": {}, "aspect": {}}
    rows = db.execute(
        "SELECT i.kind, i.key, i.keyword, i.text, t.topic "
        "FROM interpretations i LEFT JOIN interpretation_topics t ON t.interpretation_id = i.id"
    ).fetchall()
    for row in rows:
        entry = result[row["kind"]].setdefault(
            row["key"], {"keyword": row["keyword"], "text": row["text"], "topics": []}
        )
        if row["topic"]:
            entry["topics"].append(row["topic"])
    return result


# ---------------------------------------------------------------- journal notes

def _like_pattern(text):
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def add_note(db, chart_id, data):
    cursor = db.execute(
        "INSERT INTO notes (chart_id, body, content, entry_date) VALUES (?, ?, ?, ?)",
        (chart_id, data["body"], data["content"], data["entry_date"]),
    )
    db.commit()
    return cursor.lastrowid


def list_notes(db, chart_id, body=None, query=None):
    """Notes for a chart, newest entry first. body='' means whole-chart notes only."""
    sql = "SELECT * FROM notes WHERE chart_id = ?"
    params = [chart_id]
    if body == "":
        sql += " AND body IS NULL"
    elif body:
        sql += " AND body = ?"
        params.append(body)
    if query:
        sql += " AND content LIKE ? ESCAPE '\\'"
        params.append(_like_pattern(query))
    sql += " ORDER BY entry_date DESC, id DESC"
    return db.execute(sql, params).fetchall()


def get_note(db, note_id):
    return db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()


def update_note(db, note_id, data):
    db.execute(
        "UPDATE notes SET body = ?, content = ?, entry_date = ? WHERE id = ?",
        (data["body"], data["content"], data["entry_date"], note_id),
    )
    db.commit()


def delete_note(db, note_id):
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
