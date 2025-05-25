from Main import app
from Main.logging import LOGGER
from pyrogram import filters
from pyrogram.types import CallbackQuery

from Main.database.functions import get_subscription

from strings import start_txt, start_keyboard, help_txt, help_keyboard


@app.on_callback_query(filters.regex("open_help"))
async def open_help_handler(client=app, callback_query = CallbackQuery):
    try:
        await callback_query.message.edit_text(help_txt, reply_markup=help_keyboard)
    except Exception as e:
        await callback_query(f"ERROR : {e}")
        LOGGER(__name__).warning(f"⚠️ Error editing message (open_help): {e}")
        try:
            await client.send_message(
                callback_query.from_user.id, help_txt, reply_markup=help_keyboard
            )
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Error sending message (open_help): {e}")
    return


@app.on_callback_query(filters.regex("open_home"))
async def jump_to_home_handler(client=app, callback_query = CallbackQuery):
    try:
        await callback_query.message.edit_text(
            start_txt.format(callback_query.from_user.mention), reply_markup=start_keyboard
        )
    except Exception as e:
        LOGGER(__name__).warning(f"⚠️ Error editing message (jump_to_home): {e}")
        try:
            await client.send_message(
                callback_query.from_user.id,
                start_txt.format(callback_query.from_user.mention),
                reply_markup=start_keyboard
            )
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Error sending message (jump_to_home): {e}")
    return



@app.on_callback_query(filters.regex("check_usage"))
async def jump_to_home_handler(client=app, callback_query = CallbackQuery):
    user_sub = await get_subscription(callback_query.from_user.id)
    txt = f"You can send more broadcast to {user_sub} users."
    try:
        await callback_query.message.edit_text(txt)
    except Exception as e:
        LOGGER(__name__).warning(f"⚠️ Error editing message (jump_to_home): {e}")
        try:
            await client.send_message(
                callback_query.from_user.id,
                txt
            )
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Error sending message (jump_to_home): {e}")
    return

@app.on_callback_query(filters.regex("buy_subscription"))
async def jump_to_home_handler(client=app, callback_query = CallbackQuery):
    txt = f"Contact the owner to buy subscription."
    try:
        await callback_query.message.edit_text(txt)
    except Exception as e:
        LOGGER(__name__).warning(f"⚠️ Error editing message (jump_to_home): {e}")
        try:
            await client.send_message(
                callback_query.from_user.id,
                txt
            )
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Error sending message (jump_to_home): {e}")
    return