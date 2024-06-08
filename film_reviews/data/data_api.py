# (c) cat dev 2024

import requests
import sqlite3
import random
import json
import os

conn = sqlite3.connect(database="film_reviews/data/data.db", check_same_thread=False)
cur = conn.cursor()


def start():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS films (
        id INTEGER,
        name TEXT,
        review_count INTEGER
    )
    """)
    conn.commit()


def check_film(film_name):
    req_txt = ""
    for word in film_name.split(" "):
        req_txt += f"{word}_"
    req_txt += "(film)"
    req = requests.get(f"https://en.wikipedia.org/wiki/{req_txt}")
    if req.status_code == 200:
        return "Found"
    else:
        return "Not Found"


def leave_review(review_form):
    """
    global last_id
    name = review_form["film_name"]
    check = cur.execute("SELECT * FROM films WHERE name=?", (name,)).fetchone()
    if check is None:
        cur.execute("INSERT INTO films VALUES (?,?,?)", ((last_id := last_id + 1), name, 1))
        conn.commit()
        film_id = last_id
    else:
        obj = cur.execute("SELECT review_count, id FROM films WHERE name=?", (name,)).fetchone()
        review_count, film_id = obj[0], obj[1]
        cur.execute("UPDATE films SET review_count=? WHERE name=?", (review_count + 1, name))
        conn.commit()
    with open(f"../data/reviews/{film_id}_{random.randint(1000, 1000001)}.json", "w") as f:
        f.write(json.dumps(review_form))
    """


def get_reviews(film_name):
    """
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
