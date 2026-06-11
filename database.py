# database.py — Database connection and query helpers
# Job Portal Management System

import pymysql
import pymysql.cursors


# ──────────────────────────────────────────────
# DATABASE CONFIGURATION  ← edit these values
# ──────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",          # your MySQL username
    "password": "touqeer@rif311030103100",              # your MySQL password
    "database": "jobportal",
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection():
    """Return a live PyMySQL connection."""
    return pymysql.connect(**DB_CONFIG)


def execute_query(sql: str, params=None, fetch: str = "all"):
    """
    Run a SELECT and return rows.
    fetch='all'  → list of dicts
    fetch='one'  → single dict or None
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch == "one":
                return cur.fetchone()
            return cur.fetchall()
    finally:
        conn.close()


def execute_update(sql: str, params=None) -> int:
    """
    Run INSERT / UPDATE / DELETE.
    Returns the number of affected rows (or lastrowid for INSERT).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid if cur.lastrowid else cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def call_procedure(proc_name: str, args: tuple):
    """Call a stored procedure and return OUT parameters."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.callproc(proc_name, args)
            conn.commit()
            # fetch OUT param (last element)
            cur.execute("SELECT @_{}_{} AS result".format(proc_name, len(args) - 1))
            row = cur.fetchone()
            return row["result"] if row else None
    finally:
        conn.close()


def test_connection() -> bool:
    """Return True if the DB is reachable."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
