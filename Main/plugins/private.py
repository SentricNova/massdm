from Main import app
from Main.deco.user_handle import check_user

from pyrogram import filters
from pyrogram.types import Message
from strings import start_txt, start_keyboard, help_txt, help_keyboard


@app.on_message(filters.command("start") & filters.private)
@check_user
async def start_command(app, msg: Message):
    user = msg.from_user
    return await msg.reply_text(start_txt, reply_markup=start_keyboard)


@app.on_message(filters.command(["help", "guide"]) & filters.private)
@check_user
async def help_command(app, msg: Message):
    return await msg.reply_text(help_txt, reply_markup=help_keyboard)