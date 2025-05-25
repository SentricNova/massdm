from Main import app, LOGGER
from config import LOGGER_GROUP
from Main.database.functions import add_served_user

from functools import wraps
from pyrogram.types import Message


def check_user(func):
    @wraps(func)
    async def wrapper(app, message: Message, *args, **kwargs):
        user_id = message.from_user.id if message.from_user else None
        try:
            adding = await add_served_user(user_id)
            if adding == "already":
                return await func(app, message, *args, **kwargs)
            try:
                user_info = (
                    "👋 <b>NEW USER INTERACTION</b>:\n\n"
                    f"User Name: {message.from_user.mention}\n"
                    f"User ID: <code>{message.from_user.id}</code>"
                )
                if LOGGER_GROUP:
                    await app.send_message(LOGGER_GROUP, user_info)
            except Exception as err:
                LOGGER("USER LOGGING ERROR").info(f"⚠️ Error logging new user to LOGGER GROUP:\n\n{err}")
                pass
            return await func(app, message, *args, **kwargs)
        except Exception:  # Catch broad exceptions at the outer level
            return await func(app, message, *args, **kwargs)
    return wrapper