import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv library not found. Attempting to install...")
    os.system("pip3 install python-dotenv")
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Failed to install and import python-dotenv. Environment variables might not be loaded.")


# List of user IDs considered as bot owners.
BOT_OWNER = int(os.getenv("BOT_OWNER_ID"))

API_ID = int(os.getenv("API_ID"))
API_HASH = str(os.getenv("API_HASH"))
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

MONGO_DB = str(os.getenv("MONGO_DB_URI"))
DB_NAME = str(os.getenv("MONGO_DB_NAME", "Ayush"))  # Default database name is "Ayush".
LOGGER_GROUP = int(os.getenv("LOG_GROUP", False))

greetings = ["Hii", "Hellow", "Hey"]
second_msg = ["I have a work for you", "Something good for you."]
last_msg = ["Thanks buddy", "Nice. Thank uh", "Thanks a lot"]
final_msg = [greetings, second_msg]

try:
    alt_api_id = int(os.getenv("ALT_API_ID"))
    alt_api_hash = str(os.getenv("ALT_API_HASH"))
except:
    alt_api_id = API_ID
    alt_api_hash = API_HASH