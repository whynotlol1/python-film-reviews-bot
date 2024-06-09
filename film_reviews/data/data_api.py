# (c) cat dev 2024

from dotenv import load_dotenv
from os import listdir
from os import getenv
import sqlite3
import json

conn = sqlite3.connect(database="film_reviews/data/data.db", check_same_thread=False)
cur = conn.cursor()


def start():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS films (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)
    conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS moderators (
        id INTEGER
    )
    """)
    conn.commit()
    load_dotenv()
    if cur.execute("SELECT * FROM moderators WHERE id=?", (int(getenv("adminid")),)).fetchone() is None:
        cur.execute("INSERT INTO moderators VALUES (?)", (int(getenv("adminid")),))
        conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        blacklisted_id INTEGER,
        blacklisted_by INTEGER
    )
    """)
    conn.commit()


def add_moderator(*, moderator_id: int) -> str:
    check = cur.execute("SELECT * FROM moderators WHERE id=?", (moderator_id,)).fetchone()
    if check is None:
        cur.execute("INSERT INTO moderators VALUES (?)", (moderator_id,))
        conn.commit()
        return "Done."
    else:
        return "Not needed."


# TODO check if film name is valid
# def check_for_valid_film_name(name: str) -> bool:


def leave_review(*, review_form: dict):
    film_name = review_form["film_name"]
    check = cur.execute("SELECT id FROM films WHERE name=?", (film_name,)).fetchone()
    if check is None:
        cur.execute("INSERT INTO films (name) VALUES (?)", (film_name,))
        conn.commit()
        film_id = cur.execute("SELECT id FROM films WHERE name=?", (film_name,)).fetchone()[0]
    else:
        film_id = check[0]
    with open(f"film_reviews/data/reviews/{film_id}_{review_form["reviewer"]}.json", "w") as f:
        f.write(json.dumps(review_form))


def get_reviews(*, film_name: str) -> list:
    check = cur.execute("SELECT id FROM films WHERE name=?", (film_name,)).fetchone()
    if check is not None:
        film_id = check[0]
        reviews = list()
        for file_name in listdir("film_reviews/data/reviews"):
            if file_name.startswith(str(film_id)):
                with open(f"film_reviews/data/reviews/{file_name}", "r") as file:
                    reviews.append(json.loads(file.read()))
        return ["Not found"] if reviews == [] else reviews
    else:
        return ["Not found"]
