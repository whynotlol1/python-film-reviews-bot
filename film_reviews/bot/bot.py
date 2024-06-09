# (c) cat dev 2024

from film_reviews.data import data_api
from dotenv import load_dotenv
from telebot import TeleBot
from telebot import types
from os import getenv
import telebot


load_dotenv()

bot = TeleBot(token=getenv("token"))

message_texts_dir = "film_reviews/bot/message_strings"


@bot.callback_query_handler(lambda call: True)
def callback_query(call):
    if int(call.data.split("_")[0]) in range(1, 6):
        form = {
            "reviewer": call.data.split("_")[2],
            "film_name": call.data.split("_")[1].lower().title(),
            "rating": call.data.split("_")[0]
        }
        msg = bot.send_message(call.message.chat.id, f"Added your mark (<b>{int(call.data.split("_")[0])}</b>) to the review form successfully. Now, please, write the review text.", parse_mode="html")
        bot.register_next_step_handler(msg, leave_review_step2, form)


@bot.message_handler(commands=["add_moderator"])
def add_moderator(message: telebot.types.Message):
    if message.from_user.id == int(getenv("adminid")):
        bot.send_message(message.chat.id, data_api.add_moderator(moderator_id=int(message.text.split(" ")[1]), password=message.text.split(" ")[2]))
    else:
        bot.send_message(message.chat.id, "You do not have the permission to use this command!")


@bot.message_handler(commands=["start", "help"])
def help_message(message: telebot.types.Message):
    with open(f"{message_texts_dir}/help_message_text.txt", "r") as message_file:
        bot.send_message(message.chat.id, message_file.read(), parse_mode="html")


@bot.message_handler(commands=["changelog"])
def changelog_message(message: telebot.types.Message):
    with open(f"{message_texts_dir}/changelog.txt", "r") as message_file:
        bot.send_message(message.chat.id, message_file.read(), parse_mode="html")


@bot.message_handler(commands=["mod_help"])
def mod_help_message(message: telebot.types.Message):
    if data_api.check_for_mod_login(user_id=message.from_user.id):
        with open(f"{message_texts_dir}/mod_help_message_text.txt", "r") as message_file:
            bot.send_message(message.chat.id, message_file.read(), parse_mode="html")
    else:
        bot.send_message(message.chat.id, "You do not have the permission to use this command!")


@bot.message_handler(commands=["mod_login"])
def mod_login(message: telebot.types.Message):
    if data_api.can_log_in_as_mod(user_id=message.from_user.id):
        if data_api.check_for_mod_login(user_id=message.from_user.id) == 1:
            bot.send_message(message.chat.id, "You are already logged in.")
        else:
            if data_api.check_pass(user_id=message.from_user.id, password=message.text.split(" ")[1]):
                data_api.set_login_status(user_id=message.from_user.id, status=1)
                bot.send_message(message.chat.id, "Logged in as moderator successfully.")
            else:
                bot.send_message(message.chat.id, "Wrong password.")
    else:
        bot.send_message(message.chat.id, "You are not a moderator.")


@bot.message_handler(commands=["mod_logout"])
def mod_logout(message: telebot.types.Message):
    if data_api.check_for_mod_login(user_id=message.from_user.id):
        bot.send_message(message.chat.id, "Logged out successfully.")
    else:
        bot.send_message(message.chat.id, "No need to log out.")


@bot.message_handler(commands=["leave_review"])
def leave_review_step1(message: telebot.types.Message):
    args = message.text.split(" ")
    del args[0]
    if len(args) == 0:
        bot.send_message(message.chat.id, "It seems like you didn't specify the film name!")
    else:
        txt_args = ""
        for el in args:
            txt_args += f"{el} "
        film_name = txt_args[:-1]
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(text="1", callback_data=f"1_{film_name}_{message.from_user.id}"),
            types.InlineKeyboardButton(text="2", callback_data=f"2_{film_name}_{message.from_user.id}"),
            types.InlineKeyboardButton(text="3", callback_data=f"3_{film_name}_{message.from_user.id}"),
            types.InlineKeyboardButton(text="4", callback_data=f"4_{film_name}_{message.from_user.id}"),
            types.InlineKeyboardButton(text="5", callback_data=f"5_{film_name}_{message.from_user.id}")
        )
        bot.send_message(message.chat.id, "Created a review form for you. Please, rate the film 1-5 using the buttons below.", reply_markup=markup)


def leave_review_step2(message: telebot.types.Message, review_form: dict):
    review_form["review_text"] = message.text
    data_api.leave_review(review_form=review_form)
    bot.send_message(message.chat.id, "Done. Now other users can see your review.")


@bot.message_handler(commands=["read_reviews"])
def read_reviews(message: telebot.types.Message):
    args = message.text.split(" ")
    del args[0]
    if len(args) == 0:
        bot.send_message(message.chat.id, "It seems like you didn't specify the film name!")
    else:
        film_name = ""
        for el in args:
            film_name += f"{el} "
        reviews = data_api.get_reviews(film_name=film_name[:-1].lower().title())
        if reviews == ["Not found"]:
            bot.send_message(message.chat.id, f"No reviews found for film <b>{film_name[:-1].lower().title()}</b>.", parse_mode="html")
        else:
            count = 0
            for i in range(5 if len(reviews) >= 5 else len(reviews)):
                bot.send_message(message.chat.id, f"<b>Rating: {reviews[i]["rating"]}</b>\n<i>{reviews[i]["review_text"]}</i>", parse_mode="html")
                count += 1
            bot.send_message(message.chat.id, f"Above are <i>{count}</i> reviews for film <b>{film_name[:-1].lower().title()}</b>.", parse_mode="html")


@bot.message_handler(commands=["mod_read_reviews"])
def read_reviews_mod(message: telebot.types.Message):
    if data_api.check_for_mod_login(user_id=message.from_user.id):
        pass  # TODO
    else:
        bot.send_message(message.chat.id, "You do not have the permission to use this command!")


@bot.message_handler(content_types=["text"])
def on_command_error(message: telebot.types.Message):
    with open("film_reviews/data/commands.txt", "r") as commands:
        if message.text.startswith("/") and message.text.split(" ")[0] not in commands.read().split(","):
            bot.send_message(message.chat.id, "Unknown command.")
