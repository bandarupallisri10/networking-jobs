"""
SQLite database for tracking networking jobs
"""
import sqlite3
import json
from datetime import datetime
from config import DB_FILE


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            job_type TEXT,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            posted_date TEXT,
            found_date TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'new',
            applied_date TEXT,
            notes TEXT,
            UNIQUE(url)
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_at TEXT DEFAULT (datetime('now')),
            type TEXT,
            jobs_found INTEGER,
            message TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source);
        CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
        CREATE INDEX IF NOT EXISTS idx_jobs_found_date ON jobs(found_date);
    """)
    conn.commit()
    conn.close()


def upsert_job(job: dict) -> bool:
    """Insert job, skip if URL already exists. Returns True if new."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT OR IGNORE INTO jobs
                (title, company, location, salary, job_type, source, url, description, posted_date)
            VALUES
                (:title, :company, :location, :salary, :job_type, :source, :url, :description, :posted_date)
        """, job)
        inserted = cur.rowcount > 0
        conn.commit()
        return inserted
    except Exception as e:
        print(f"[DB] Error inserting job: {e}")
        return False
    finally:
        conn.close()


def get_jobs(status=None, source=None, limit=200, offset=0, search=None):
    conn = get_connection()
    cur = conn.cursor()
    conditions = []
    params = []
    if status:
        conditions.append("status = ?")
        params.append(status)
    if source:
        conditions.append("source = ?")
        params.append(source)
    if search:
        conditions.append("(title LIKE ? OR company LIKE ? OR location LIKE ?)")
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params += [limit, offset]
    cur.execute(f"""
        SELECT * FROM jobs {where}
        ORDER BY found_date DESC
        LIMIT ? OFFSET ?
    """, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_job_by_id(job_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_job_status(job_id: int, status: str, notes: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if status == "applied":
        cur.execute("""
            UPDATE jobs SET status=?, applied_date=datetime('now'), notes=?
            WHERE id=?
        """, (status, notes, job_id))
    else:
        cur.execute("UPDATE jobs SET status=?, notes=? WHERE id=?", (status, notes, job_id))
    conn.commit()
    conn.close()


def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status='new' THEN 1 ELSE 0 END) as new_jobs,
            SUM(CASE WHEN status='applied' THEN 1 ELSE 0 END) as applied,
            SUM(CASE WHEN status='saved' THEN 1 ELSE 0 END) as saved,
            SUM(CASE WHEN status='rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN DATE(found_date)=DATE('now') THEN 1 ELSE 0 END) as today
        FROM jobs
    """)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}


def get_sources_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT source, COUNT(*) as count
        FROM jobs
        GROUP BY source
        ORDER BY count DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_notification(notif_type: str, jobs_found: int, message: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (type, jobs_found, message)
        VALUES (?, ?, ?)
    """, (notif_type, jobs_found, message))
    conn.commit()
    conn.close()
