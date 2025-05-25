# Import necessary modules and classes from within the project.
from Main.logging import LOGGER
from Main.core.bot import botClient
from Main.core.mongo import mongodb

# Initialize the Telegram bot client.
app = botClient()

db = mongodb