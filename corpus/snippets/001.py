"""Analytics helper: return the top spenders from a SQLite spend table."""

import sqlite3


def top_spenders(db_path, limit):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT user, total FROM spend ORDER BY total DESC LIMIT " + str(limit))
    rows = cur.fetchall()

    result = {}
    for user, total in rows:
        result[total] = user

    conn.close()
    return result
