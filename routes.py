from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from . import astro, interpret, journal, repository
from .db import get_db

bp = Blueprint("main", __name__)


# ------------------------------------------------------------------ charts

@bp.get("/")
def index():
    db = get_db()
    return render_template(
        "index.html",
        summaries=repository.list_charts(db),
        has_sample=repository.has_sample(db),
        demo=astro.wheel_data(astro.SAMPLE_PLACEMENTS),
    )


@bp.route("/charts/new", methods=("GET", "POST"))
def new_chart():
    context = {"bodies": astro.BODIES, "signs": astro.SIGNS, "errors": [], "form": {}}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        errors = []
        if not name:
            errors.append("Give the chart a name.")
        elif len(name) > 80:
            errors.append("The name is too long (80 characters maximum).")

        details, detail_errors = astro.parse_birth_details(request.form)
        placements, placement_errors = astro.parse_placements(request.form)
        errors += detail_errors + placement_errors

        if not errors:
            chart_id = repository.create_chart(get_db(), name, details, placements)
            flash("Chart saved.")
            return redirect(url_for("main.view_chart", chart_id=chart_id))

        context.update(errors=errors, form=request.form)
        return render_template("new_chart.html", **context), 400

    return render_template("new_chart.html", **context)


@bp.get("/charts/<int:chart_id>")
def view_chart(chart_id):
    db = get_db()
    chart = repository.get_chart(db, chart_id)
    if chart is None:
        abort(404)

    wheel = astro.wheel_data(repository.get_placements(db, chart_id))
    readings = interpret.build_readings(wheel, repository.get_interpretations(db))

    notes_by_body = {}
    for note in repository.list_notes(db, chart_id):
        notes_by_body.setdefault(note["body"] or "", []).append(
            {"id": note["id"], "content": note["content"], "entryDate": note["entry_date"]}
        )

    return render_template(
        "chart.html",
        chart=chart,
        wheel=wheel,
        topics=interpret.topics_in_use(readings),
        reading_data={"readings": readings, "notes": notes_by_body},
    )


@bp.post("/charts/<int:chart_id>/delete")
def delete_chart(chart_id):
    db = get_db()
    if repository.get_chart(db, chart_id) is None:
        abort(404)
    repository.delete_chart(db, chart_id)
    flash("Chart deleted.")
    return redirect(url_for("main.index"))


@bp.post("/charts/sample")
def load_sample():
    db = get_db()
    if repository.has_sample(db):
        flash("The sample chart is already loaded.")
        return redirect(url_for("main.index"))
    chart_id = repository.create_chart(
        db, "Sample chart (fictional)", {}, astro.SAMPLE_PLACEMENTS, is_sample=True
    )
    return redirect(url_for("main.view_chart", chart_id=chart_id))


# ------------------------------------------------------------------ journal

def _redirect_after_note(chart_id, body):
    """Only ever redirect to our own pages, chosen from a fixed set."""
    if request.form.get("return_to") == "chart":
        if body:
            return redirect(url_for("main.view_chart", chart_id=chart_id, body=body) + "#reading")
        return redirect(url_for("main.view_chart", chart_id=chart_id))
    return redirect(url_for("main.journal_page", chart_id=chart_id))


@bp.get("/charts/<int:chart_id>/journal")
def journal_page(chart_id):
    db = get_db()
    chart = repository.get_chart(db, chart_id)
    if chart is None:
        abort(404)

    # "all" shows everything, "chart" only whole-chart notes, otherwise one placement.
    selected = request.args.get("body", "all")
    body = None if selected == "all" else "" if selected == "chart" else selected
    query = request.args.get("q", "").strip()
    notes = repository.list_notes(db, chart_id, body=body, query=query or None)
    return render_template(
        "journal.html",
        chart=chart,
        notes=notes,
        bodies=astro.BODIES,
        selected_body=selected,
        query=query,
        total=len(repository.list_notes(db, chart_id)),
    )


@bp.post("/charts/<int:chart_id>/notes")
def add_note(chart_id):
    db = get_db()
    if repository.get_chart(db, chart_id) is None:
        abort(404)

    data, errors = journal.parse_note(request.form)
    if errors:
        for error in errors:
            flash(error)
        return _redirect_after_note(chart_id, data["body"])

    repository.add_note(db, chart_id, data)
    flash("Note saved.")
    return _redirect_after_note(chart_id, data["body"])


@bp.route("/notes/<int:note_id>/edit", methods=("GET", "POST"))
def edit_note(note_id):
    db = get_db()
    note = repository.get_note(db, note_id)
    if note is None:
        abort(404)

    if request.method == "POST":
        data, errors = journal.parse_note(request.form)
        if not errors:
            repository.update_note(db, note_id, data)
            flash("Note updated.")
            return redirect(url_for("main.journal_page", chart_id=note["chart_id"]))
        note = {"id": note_id, "chart_id": note["chart_id"], **data}
        return render_template("edit_note.html", note=note, bodies=astro.BODIES, errors=errors), 400

    return render_template("edit_note.html", note=note, bodies=astro.BODIES, errors=[])


@bp.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    db = get_db()
    note = repository.get_note(db, note_id)
    if note is None:
        abort(404)
    repository.delete_note(db, note_id)
    flash("Note deleted.")
    return redirect(url_for("main.journal_page", chart_id=note["chart_id"]))


@bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
