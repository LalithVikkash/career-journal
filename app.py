from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("career_journal.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            skill TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    search = request.args.get("search", "")

    conn = sqlite3.connect("career_journal.db")
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM entries
            WHERE title LIKE ? OR skill LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM entries ORDER BY id DESC")

    entries = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM entries")
    total_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'Completed'")
    completed_entries = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'In Progress'")
    in_progress_entries = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        entries=entries,
        total_entries=total_entries,
        completed_entries=completed_entries,
        in_progress_entries=in_progress_entries,
        search=search
    )

@app.route("/add", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        title = request.form["title"]
        skill = request.form["skill"]
        description = request.form["description"]
        status = request.form["status"]

        conn = sqlite3.connect("career_journal.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO entries (title, skill, description, status)
            VALUES (?, ?, ?, ?)
        """, (title, skill, description, status))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_entry.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_entry(id):
    conn = sqlite3.connect("career_journal.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        skill = request.form["skill"]
        description = request.form["description"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE entries
            SET title = ?, skill = ?, description = ?, status = ?
            WHERE id = ?
        """, (title, skill, description, status, id))

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute("SELECT * FROM entries WHERE id = ?", (id,))
    entry = cursor.fetchone()

    conn.close()

    return render_template("edit_entry.html", entry=entry)

@app.route("/delete/<int:id>")
def delete_entry(id):
    conn = sqlite3.connect("career_journal.db")
    cursor = conn.cursor()

    cursor