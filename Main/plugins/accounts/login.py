import asyncio
from Main import app
from config import BOT_OWNER
from pyrogram import filters, Client
from pyrogram.types import Message

from Main.plugins.accounts.scrapper import members
from Main.plugins.accounts.gen import generate_session, run_client
from Main.database.functions import get_all_account, add_subscription, idle_userbots, get_updated_served_users

from config import alt_api_id, alt_api_hash

session = []

@app.on_message(filters.command("login") & filters.user(BOT_OWNER))
async def login(app, msg: Message):
    splited_txt = msg.text.split(" ")
    if len(splited_txt) >= 2:
        session_string = splited_txt[-1]
        if len(session_string) > 30:
            if session_string in session:
                return await msg.reply_text("This session is already running.")
            session.append(session_string)
            try:
                ok = await run_client(alt_api_id, alt_api_hash, session_string, msg)
                return
            except Exception as err:
                return await msg.reply_text(f"An error occurred while running the client with the session string:\n\n{err}")
    
    try:
        await generate_session(app, msg, msg.from_user)
    except Exception as err:
        return await msg.reply_text(f"An error occurred in the login function:\n\n{err}")

@app.on_message(filters.command("login_all") & filters.user(BOT_OWNER))
async def login_all(app, message: Message):
    info = await message.reply_text("Loading all clients from the database...")
    userbots = await get_all_account()

    if len(userbots) <= 0:
        return await info.edit_text("You don't have any userbots. Please log in to an account to add it to your database.")

    await info.edit_text(f"{len(userbots)} userbots loaded successfully!")

    tasks = [
        asyncio.create_task(run_client(data["api_id"], data["api_hash"], data["string_session"], message))
        for data in userbots
    ]
    await asyncio.gather(*tasks)

    return await info.edit_text(f"{len(idle_userbots)} userbots have been started successfully!")

@app.on_message(filters.command(["stats", "stat"]) & filters.user(BOT_OWNER))
async def stats(app, message: Message):
    info = await message.reply_text("Please wait, loading bot statistics...")
    ubs = len(idle_userbots)
    total_users = len(await get_updated_served_users())
    total_members = len(members)
    stats_text = f"""BOT STATISTICS:\n\nUser bots: {ubs}\nServed Users: {total_users}\nTotal Scraped Members: {total_members}"""
    return await info.edit_text(stats_text)

@app.on_message(filters.command(["add", "sub"]) & filters.user(BOT_OWNER))
async def add_subscription_command(app, message: Message):
    splited_text = message.text.split(" ")
    if len(splited_text) <= 2:
        return await message.reply_text("USAGE:\n`/sub user_id number_of_quota`")
    
    try:
        quota_number = int(splited_text[-1])
        user_id = int(splited_text[-2])
    except Exception as err:
        return await message.reply_text(f"Error: {err}")
    
    try:
        await add_subscription(user_id, quota_number)
        return await message.reply_text(f"<b>SUBSCRIPTION SUCCESSFUL ✅</b>\nUser  ID: {user_id}\nQuota: {quota_number}")
    except Exception as err:
        return await message.reply_text(f"<b>Something went wrong:</b>\n{str(err)}")
