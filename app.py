
import os
import time
import mysql.connector
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "todo_user"),
        password=os.getenv("DB_PASSWORD", "todo_pass"),
        database=os.getenv("DB_NAME", "todo_db")
    )

def init_db():
    for attempt in range(30):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return
        except mysql.connector.Error:
            time.sleep(2)
    raise RuntimeError("Database MySQL tidak dapat dihubungi")

HTML = """
<!doctype html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>To-Do List</title>
</head>
<body>
    <h1>To-Do List</h1>
    <p>Aplikasi Flask dengan database MySQL dan Docker.</p>
    <form method="post" action="/add">
        <input name="title" placeholder="Masukkan tugas" required>
        <button type="submit">Tambah</button>
    </form>
    <ul>
    {% for task in tasks %}
        <li>
            {{ task[1] }}
            <form method="post" action="/delete/{{ task[0] }}"
                  style="display:inline">
                <button type="submit">Hapus</button>
            </form>
        </li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(HTML, tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect("/")

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

