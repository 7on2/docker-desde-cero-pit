import os

import psycopg2
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")


def get_db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        port=os.environ.get("DB_PORT", "5432"),
    )


@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, titulo, completado FROM tareas ORDER BY id")
    tareas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", tareas=tareas)


@app.route("/health")
def health():
    conn = get_db()
    conn.close()
    return jsonify({"status": "healthy"})


@app.route("/tareas", methods=["POST"])
def crear_tarea():
    data = request.get_json(force=True)
    titulo = data.get("titulo", "").strip()
    if not titulo:
        return jsonify({"error": "titulo requerido"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tareas (titulo) VALUES (%s)", (titulo,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 201


@app.route("/tareas/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tareas WHERE id = %s", (tarea_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
