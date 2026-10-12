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
