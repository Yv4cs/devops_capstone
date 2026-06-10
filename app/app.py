import os
import time

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, render_template
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__)

# Tự phơi GET /metrics và tự đếm MỌI HTTP request
# (tạo các series flask_http_request_total, _duration_seconds...).
metrics = PrometheusMetrics(app)
metrics.info("notes_app_info", "Notes application", version="1.0.0")

# Metric "nghiệp vụ" tự định nghĩa: tổng số note đã tạo thành công.
notes_created_total = Counter(
    "notes_created_total", "Total number of notes successfully created"
)

# Database connection settings come from environment variables.
# Defaults match docker-compose.yml so it "just works" locally.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "notesdb"),
    "user": os.getenv("DB_USER", "notes"),
    "password": os.getenv("DB_PASSWORD", "notes"),
}


def get_conn():
    """Open a new database connection."""
    return psycopg2.connect(cursor_factory=RealDictCursor, **DB_CONFIG)


def init_db():
    """Create the notes table. Retries because the DB container may
    take a few seconds to become ready when the stack first starts."""
    for attempt in range(15):
        try:
            conn = get_conn()
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """
                )
            conn.close()
            print("Database is ready.")
            return
        except psycopg2.OperationalError as exc:
            print(f"Database not ready (attempt {attempt + 1}/15): {exc}")
            time.sleep(2)
    raise RuntimeError("Could not connect to the database.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    # Kubernetes will use this endpoint for liveness/readiness probes later.
    return jsonify(status="ok"), 200


@app.route("/api/notes", methods=["GET"])
def list_notes():
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        notes = cur.fetchall()
    conn.close()
    return jsonify(notes)


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify(error="content is required"), 400
    conn = get_conn()
    with conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO notes (content) VALUES (%s) RETURNING id, content, created_at",
            (content,),
        )
        note = cur.fetchone()
    conn.close()
    notes_created_total.inc()   # +1 mỗi khi tạo note thành công
    return jsonify(note), 201


# Initialise the database when the module is imported (works with gunicorn too).
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)