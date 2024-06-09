# (c) cat dev 2024

from dotenv import load_dotenv
from os import getenv
import sqlite3
import random
import string
import json

conn = sqlite3.connect(database="film_reviews/data/data.db", check_same_thread=False)
cur = conn.cursor()


def to_str(_a: list):
    _b: str = ""
    for el in _a:
        _b += el
    return _b


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
    cur.execute(f"INSERT INTO moderators VALUES ({int(getenv("adminid"))})")
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
    with open(f"film_reviews/data/reviews/{film_id}_{to_str(random.sample(string.ascii_letters, random.randint(15, 25)))}", "w") as f:
        f.write(json.dumps(review_form))


"""
def get_reviews(*, film_name: str):
    check = cur.execute("SELECT * FROM films WHERE name=?", (film_name,)).fetchone()
    if check is not None:
        obj = cur.execute("SELECT id FROM films WHERE name=?", (film_name,)).fetchone()
        film_id = obj[0]
        reviews = {}
        for num in range(1000, 1000001):
            path = f"../data/reviews/{film_id}_{num}.json"
            if os.path.isfile(path):
                with open(path, "r") as f:
                    json_obj = json.loads(f.read())
                    reviews[json_obj["rating"]] = json_obj["review_text"]
        return reviews
    else:
        return None
    """
