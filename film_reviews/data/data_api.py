# (c) cat dev 2024

from dotenv import load_dotenv
from hashlib import sha512
from os import listdir
from os import remove
from os import getenv
from os import mkdir
from os import path
import requests
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviewers (
            id INTEGER,
            reviews INTEGER
        )
        """)
    conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS moderators (
        id INTEGER,
        password TEXT,
        login_status INTEGER
    )
    """)
    conn.commit()
    load_dotenv()
    if cur.execute("SELECT * FROM moderators WHERE id=?", (int(getenv("adminid")),)).fetchone() is None:
        cur.execute("INSERT INTO moderators VALUES (?, ?, ?)", (int(getenv("adminid")), "ALWAYS LOGGED IN", 1))
        conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        blacklisted_id INTEGER,
        blacklisted_by INTEGER
    )
    """)
    conn.commit()
    if not path.isdir("film_reviews/data/reviews"):
        mkdir("film_reviews/data/reviews")


def add_moderator(*, moderator_id: int, password: str) -> str:
    check = cur.execute("SELECT * FROM moderators WHERE id=?", (moderator_id,)).fetchone()
    if check is None:
        cur.execute("INSERT INTO moderators VALUES (?, ?, ?)", (moderator_id, sha512(password.encode()).hexdigest(), 0))
        conn.commit()
        return "Done."
    else:
        return "Not needed."


def can_log_in_as_mod(*, user_id: int) -> bool:
    check = cur.execute("SELECT * FROM moderators WHERE id=?", (user_id,)).fetchone()
    return check is not None


def check_for_mod_login(*, user_id: int) -> bool:
    check = cur.execute("SELECT login_status FROM moderators WHERE id=?", (user_id,)).fetchone()
    return check[0] == 1


def check_pass(*, user_id: int, password: str) -> bool:
    check = cur.execute("SELECT password FROM moderators WHERE id=?", (user_id,)).fetchone()
    return sha512(password.encode()).hexdigest() == check[0]


def set_login_status(*, user_id: int, status: int):
    check = cur.execute("SELECT password FROM moderators WHERE id=?", (user_id,)).fetchone()
    if check[0] != "ALWAYS LOGGED IN":
        cur.execute("UPDATE moderators SET login_status=? WHERE id=?", (status, user_id))
        conn.commit()


def blacklist_action(*, action: str, user_id: int, mod_id: int):
    match action:
        case "add":
            cur.execute("INSERT INTO blacklist VALUES (?,?)", (user_id, mod_id))
        case "remove":
            cur.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
    conn.commit()


def get_blacklist() -> str:
    check = cur.execute("SELECT * FROM blacklist").fetchone()
    blacklist_str = "<i>Note: the list is only telegram IDs. No names etc.</i>\nBlacklist:\n"
    if check is not None:
        blacklist = cur.execute("SELECT * FROM blacklist").fetchall()
        for el in blacklist:
            blacklist_str += f"<b>{el[0]}</b> | <i>Blacklisted by {el[1]}</i>\n"
    else:
        blacklist_str += "<b>~ E M P T Y ~</b>"
    return blacklist_str


def user_in_blacklist(*, user_id: int) -> bool:
    check = cur.execute("SELECT * FROM blacklist WHERE blacklisted_id=?", (user_id,)).fetchone()
    return check is not None


def check_for_valid_film_name(*, film_name: str) -> bool:
    base_url = "http://www.omdbapi.com/"
    params = {
        "apikey": getenv("omdbkey"),
        "t": film_name
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["Response"] == "True"
    else:
        return False


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
    check = cur.execute("SELECT reviews FROM reviewers WHERE id=?", (review_form["reviewer"],)).fetchone()
    if check is None:
        cur.execute("INSERT INTO reviewers VALUES (?, ?)", (review_form["reviewer"], 1))
        conn.commit()
    else:
        cur.execute("UPDATE reviewers SET reviews=? WHERE id=?", (check[0] + 1, review_form["reviewer"]))
        conn.commit()


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


def get_user_profile(*, user_id: int) -> list:
    check = cur.execute("SELECT reviews FROM reviewers WHERE id=?", (user_id,)).fetchone()
    if check is None:
        return ["no", can_log_in_as_mod(user_id=user_id)]
    else:
        return [f"{check[0]}", can_log_in_as_mod(user_id=user_id)]


def delete_review(*, user_id: int, film_name: str):
    film_id = cur.execute("SELECT id FROM films WHERE name=?", (film_name,)).fetchone()[0]
    file_name = f"{film_id}_{user_id}.json"
    remove(f"film_reviews/data/reviews/{file_name}")
