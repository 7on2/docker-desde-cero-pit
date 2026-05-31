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


@app.route("/")
def home():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
    return f"Flask conectado a PostgreSQL: {version}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
