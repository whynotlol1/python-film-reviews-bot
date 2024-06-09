# (c) cat dev 2024

from requests import exceptions
from film_reviews.data import data_api
from film_reviews.bot.bot import bot
import sys
import os

if __name__ == "__main__":
    print("Bot is running...")
    data_api.start()
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (exceptions.ConnectionError, exceptions.ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
