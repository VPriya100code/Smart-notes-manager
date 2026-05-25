from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "notes.db"


# CREATE DATABASE TABLE
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            important INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# HOME PAGE
@app.route("/")
def index():
    search = request.args.get("search", "")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY important DESC, id DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("""
            SELECT * FROM notes
            ORDER BY important DESC, id DESC
        """)

    notes = cursor.fetchall()

    conn.close()

    return render_template("index.html", notes=notes, search=search)


# ADD NOTE
@app.route("/add", methods=["POST"])
def add_note():
    title = request.form["title"].strip()
    content = request.form["content"].strip()
    important = 1 if request.form.get("important") else 0

    # EDGE CASE HANDLING
    if not title or not content:
        return redirect("/")

    created_at = datetime.now().strftime("%d %b %Y %I:%M %p")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notes (title, content, important, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, content, important, created_at))

    conn.commit()
    conn.close()

    return redirect("/")


# DELETE NOTE
@app.route("/delete/<int:note_id>")
def delete_note(note_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    conn.commit()
    conn.close()

    return redirect("/")


# TOGGLE IMPORTANT
@app.route("/important/<int:note_id>")
def toggle_important(note_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notes
        SET important = CASE
            WHEN important = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (note_id,))

    conn.commit()
    conn.close()

    return redirect("/")


# EDIT NOTE
@app.route("/edit/<int:note_id>", methods=["POST"])
def edit_note(note_id):
    title = request.form["title"].strip()
    content = request.form["content"].strip()

    if not title or not content:
        return redirect("/")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notes
        SET title = ?, content = ?
        WHERE id = ?
    """, (title, content, note_id))

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)