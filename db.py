import sqlite3

from flask import current_app, g


def get_db():
    """One SQLite connection per request, with foreign keys switched on."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    """Create the tables if they do not exist yet (safe to run on every start)."""
    connection = get_db()
    with current_app.open_resource("schema.sql") as f:
        connection.executescript(f.read().decode("utf8"))


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
