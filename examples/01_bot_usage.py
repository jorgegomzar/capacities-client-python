import logging
from dotenv import load_dotenv

from capacities.bot import CapacitiesTelegramBot


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # this is to load env variables from a .env file
    load_dotenv()

    bot = CapacitiesTelegramBot()
    bot.run()
