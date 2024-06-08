from film_reviews.data import data_api
from film_reviews.bot.bot import bot

if __name__ == "__main__":
    print("Bot is running...")
    data_api.start()
    bot.polling(none_stop=True)
