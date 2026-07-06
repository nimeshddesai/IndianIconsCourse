from __future__ import annotations

import json
import mimetypes
import os
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "indian_icons_course.db"


class CourseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/course":
            self.send_json(load_course_summary())
            return

        if path.startswith("/api/modules/"):
            module_id = unquote(path.removeprefix("/api/modules/"))
            module = load_module(module_id)
            if module is None:
                self.send_error(404, "Module not found")
                return
            self.send_json(module)
            return

        if path == "/health":
            self.send_json({"ok": True, "database": DB_PATH.exists()})
            return

        return super().do_GET()

    def send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def connect():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run scripts/seed_db.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_course_summary():
    with connect() as conn:
        course = conn.execute("SELECT * FROM courses ORDER BY id LIMIT 1").fetchone()
        modules = conn.execute(
            """
            SELECT m.*, COUNT(l.id) AS lesson_count
            FROM modules m
            LEFT JOIN lessons l ON l.module_id = m.id
            WHERE m.course_id = ?
            GROUP BY m.id
            ORDER BY m.sort_order
            """,
            (course["id"],),
        ).fetchall()

        module_payload = []
        for module in modules:
            lessons = conn.execute(
                """
                SELECT id, hero, years, value
                FROM lessons
                WHERE module_id = ?
                ORDER BY sort_order
                """,
                (module["id"],),
            ).fetchall()
            module_payload.append(
                {
                    "id": module["id"],
                    "week": module["week"],
                    "title": module["title"],
                    "focus": module["focus"],
                    "activity": module["activity"],
                    "challenge": module["challenge"],
                    "lessons": [dict(row) for row in lessons],
                }
            )

        return {
            "id": course["id"],
            "title": course["title"],
            "subtitle": course["subtitle"],
            "sourceNote": course["source_note"],
            "modules": module_payload,
        }


def load_module(module_id):
    with connect() as conn:
        module = conn.execute(
            "SELECT * FROM modules WHERE id = ?",
            (module_id,),
        ).fetchone()
        if module is None:
            return None

        lessons = conn.execute(
            """
            SELECT *
            FROM lessons
            WHERE module_id = ?
            ORDER BY sort_order
            """,
            (module_id,),
        ).fetchall()

        lesson_payload = []
        for lesson in lessons:
            blocks = conn.execute(
                """
                SELECT title, body
                FROM story_blocks
                WHERE lesson_id = ?
                ORDER BY sort_order
                """,
                (lesson["id"],),
            ).fetchall()
            questions = conn.execute(
                """
                SELECT *
                FROM quiz_questions
                WHERE lesson_id = ?
                ORDER BY sort_order
                """,
                (lesson["id"],),
            ).fetchall()

            quiz = []
            for question in questions:
                options = conn.execute(
                    """
                    SELECT option_text
                    FROM quiz_options
                    WHERE question_id = ?
                    ORDER BY sort_order
                    """,
                    (question["id"],),
                ).fetchall()
                quiz.append(
                    {
                        "type": question["question_type"],
                        "question": question["question"],
                        "answer": question["answer_index"],
                        "options": [row["option_text"] for row in options],
                    }
                )

            lesson_payload.append(
                {
                    "id": lesson["id"],
                    "hero": lesson["hero"],
                    "years": lesson["years"],
                    "value": lesson["value"],
                    "link": lesson["link"],
                    "hook": lesson["hook"],
                    "lifeStory": lesson["life_story"],
                    "blocks": [[row["title"], row["body"]] for row in blocks],
                    "reflection": lesson["reflection"],
                    "quiz": quiz,
                }
            )

        return {
            "id": module["id"],
            "week": module["week"],
            "title": module["title"],
            "focus": module["focus"],
            "activity": module["activity"],
            "challenge": module["challenge"],
            "lessons": lesson_payload,
        }


def main():
    mimetypes.add_type("text/javascript", ".js")
    mimetypes.add_type("image/x-icon", ".ico")
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), CourseHandler)
    print(f"Indian Icons Story Course running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
