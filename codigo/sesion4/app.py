import os

import psycopg
from flask import Flask


app = Flask(__name__)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "appsecret"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT now()
                );
                """
            )


@app.route("/")
def home():
    init_db()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM visits;")
            total = cur.fetchone()[0]
    return f"Flask + PostgreSQL funcionando. Registros persistentes: {total}"


@app.route("/add")
def add_visit():
    init_db()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO visits DEFAULT VALUES RETURNING id;")
            visit_id = cur.fetchone()[0]
    return f"Registro persistente creado: {visit_id}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
