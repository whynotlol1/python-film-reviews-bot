# (c) cat dev 2024

from film_reviews.data import data_tools as dt
from telebot import types
import telebot

with open("../data/token.txt", "r") as token_file:
    bot = telebot.TeleBot(token_file.read())


@bot.callback_query_handler(lambda call: True)
def callback_query(call):
    if int(call.data.split(" ")[0]) in range(1, 6):
        form = {
            "film_name": call.data.lower()[2:].title(),
            "rating": call.data.split(" ")[0]
        }
        msg = bot.send_message(call.message.chat.id, f"Added your mark ({int(call.data.split(" ")[0])}) to the review form successfully. Now, please, write the review text.")
        bot.register_next_step_handler(msg, leave_review_step2, form)


@bot.message_handler(commands=["start", "help"])
def help_message(message):
    with open("long_strings/help_message_text.txt", "r") as f:
        bot.send_message(message.from_user.id, f.read())


@bot.message_handler(commands=["changelog"])
def changelog_message(message):
    with open("long_strings/changelog.txt", "r") as f:
        bot.send_message(message.from_user.id, f.read())


@bot.message_handler(commands=["report_bug"])
def report_bug_step1(message):
    msg = bot.send_message(message.from_user.id, "Please, describe the bug or issue you have found.")
    bot.register_next_step_handler(msg, report_bug_step2)


def report_bug_step2(message):
    dt.cur.execute("INSERT INTO bugs VALUES (?)", (message.text,))
    dt.conn.commit()
    bot.send_message(message.from_user.id, "Thank you for your feedback. This bug or issue will be fixed soon.")


@bot.message_handler(commands=["read_reviews"])
def read_reviews_step1(message):
    args = message.text.split(" ")
    del args[0]
    if len(args) == 0:
        bot.send_message(message.from_user.id, "It seems like you didn't specify the film name!")
    else:
        txt_args = ""
        for el in args:
            txt_args += f"{el} "
        film_name = txt_args[:-1]
        if dt.check_film(film_name.lower().title()) != "Not Found":
            if dt.get_reviews(film_name.lower().title()) is not None:
                bot.send_message(message.from_user.id, "Now the bot will send all the reviews found for that film.")
                for rating, text in dt.get_reviews(film_name.lower().title()).items():
                    bot.send_message(message.from_user.id, f"Rating: {rating}\n\n{text}")
            else:
                bot.send_message(message.from_user.id, "It seems like other users haven't left any reviews on that film yet.")
        else:
            bot.send_message(message.from_user.id, "Sorry but it seems like this film does not exist.")


@bot.message_handler(commands=["leave_review"])
def leave_review_step1(message):
    args = message.text.split(" ")
    del args[0]
    if len(args) == 0:
        bot.send_message(message.from_user.id, "It seems like you didn't specify the film name!")
    else:
        txt_args = ""
        for el in args:
            txt_args += f"{el} "
        film_name = txt_args[:-1]
        if dt.check_film(film_name.lower().title()) != "Not Found":
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(text="1", callback_data=f"1 {film_name}"),
                types.InlineKeyboardButton(text="2", callback_data=f"2 {film_name}"),
                types.InlineKeyboardButton(text="3", callback_data=f"3 {film_name}"),
                types.InlineKeyboardButton(text="4", callback_data=f"4 {film_name}"),
                types.InlineKeyboardButton(text="5", callback_data=f"5 {film_name}")
            )
            bot.send_message(message.from_user.id, "Created a review form for you. Please, rate the film 1-5 using the buttons below.", reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, "Sorry but it seems like this film does not exist.")


def leave_review_step2(message, review_form):
    review_form["review_text"] = message.text
    dt.leave_review(review_form)
    bot.send_message(message.from_user.id, "Done. Now other users can see your review.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
