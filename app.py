import os
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone
from flask import Flask, request, redirect, url_for, render_template, send_file, abort, flash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def cleanup_expired():
    now = datetime.now(timezone.utc)
    conn = get_db()
    rows = conn.execute(
        "SELECT stored_name FROM files WHERE expires_at <= ?",
        (now.isoformat(),)
    ).fetchall()

    for row in rows:
        path = os.path.join(UPLOAD_FOLDER, row["stored_name"])
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass

    conn.execute("DELETE FROM files WHERE expires_at <= ?", (now.isoformat(),))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    cleanup_expired()
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    cleanup_expired()

    if "file" not in request.files:
        flash("Please select a file.")
        return redirect(url_for("index"))

    file = request.files["file"]
    if not file or not file.filename:
        flash("Please select a file.")
        return redirect(url_for("index"))

    original_name = secure_filename(file.filename)
    if not original_name:
        flash("Invalid filename.")
        return redirect(url_for("index"))

    token = secrets.token_urlsafe(18)
    stored_name = f"{token}_{original_name}"
    file.save(os.path.join(UPLOAD_FOLDER, stored_name))

    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)

    conn = get_db()
    conn.execute("""
        INSERT INTO files
        (token, original_name, stored_name, uploaded_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (token, original_name, stored_name, now.isoformat(), expires.isoformat()))
    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        download_url=url_for("download", token=token, _external=True),
        expires_at=expires.strftime("%d %b %Y, %I:%M %p UTC")
    )

@app.route("/download/<token>")
def download(token):
    cleanup_expired()

    conn = get_db()
    row = conn.execute("SELECT * FROM files WHERE token = ?", (token,)).fetchone()
    conn.close()

    if row is None:
        abort(404, description="This link is invalid or has expired.")

    expires = datetime.fromisoformat(row["expires_at"])
    if datetime.now(timezone.utc) >= expires:
        cleanup_expired()
        abort(410, description="This download link has expired.")

    path = os.path.join(UPLOAD_FOLDER, row["stored_name"])
    if not os.path.isfile(path):
        abort(404, description="The file is no longer available.")

    return send_file(path, as_attachment=True, download_name=row["original_name"])

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404,
                           message=getattr(error, "description", "Page not found.")), 404

@app.errorhandler(410)
def gone(error):
    return render_template("error.html", code=410,
                           message=getattr(error, "description", "This link has expired.")), 410

@app.errorhandler(413)
def too_large(error):
    return render_template("error.html", code=413,
                           message="File is too large. Maximum size is 100 MB."), 413

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
