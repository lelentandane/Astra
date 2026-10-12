from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from . import astro, repository
from .db import get_db

bp = Blueprint("main", __name__)


def ordinal(n):
    """1 -> 1st, 2 -> 2nd, 11 -> 11th. Used for house numbers in templates."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


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
    return render_template("chart.html", chart=chart, wheel=wheel)


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


@bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
