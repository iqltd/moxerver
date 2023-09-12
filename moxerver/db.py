import os
import sqlite3
from flask import g

DB_PATH = "db"
DB_FILE = "history.db"


def ensure_path():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        database = os.path.join(DB_PATH, DB_FILE)
        db = g._database = sqlite3.connect(database)

    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
