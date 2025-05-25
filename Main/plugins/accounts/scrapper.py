import pickle
from config import BOT_OWNER
from Main import app
from pyrogram import filters
from pyrogram.types import Message
from Main.database.functions import idle_userbots as userbots

members = ["h_ayush"]
temp_members = []

def get_group_id_username(link_text: str):
    if link_text.startswith("https://t.me/+"):
        return link_text, "private_gc", False
    elif link_text.startswith("@") or link_text.startswith("https://t.me/"):
        return link_text, "public_gc", False
    elif link_text.isdigit():
        try:
            return int(link_text), "private_gc_id", False
        except Exception as err:
            return False, False, err
    else:
        return False, False, "The provided group ID is not a valid ID or username. Please double-check it."

def backup_member_list(data_list, filename="members_backup.pkl"):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(data_list, f)
        try:
            temp_members.extend(data_list)
            temp_members.extend(members)
            members.clear()
            unique_list = list(set(temp_members))
            members.extend(unique_list)
        except Exception as err:
            print(err)
        return filename
    except Exception as e:
        print(f"Error: {e}")
        return False

def restore_member_list(filename="backup.pkl"):
    try:
        with open(filename, 'rb') as f:
            restored_list = pickle.load(f)
        try:
            temp_members.extend(restored_list)
            temp_members.extend(members)
            members.clear()
            unique_list = list(set(temp_members))
            members.extend(unique_list)
        except Exception as err:
            print(err)
        return restored_list
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

@app.on_message(filters.command("scrape") & filters.user(BOT_OWNER))
async def scrape(app, message: Message):
    splited_text = message.text.split(" ")
    if len(splited_text) <= 1:
        return await message.reply_text("Incorrect usage! Please learn how to use it:\n\n/scrape any_group_link_username")
    
    group_id, group_type, any_error = get_group_id_username(splited_text[-1])
    if group_id is False:
        return await message.reply_text(any_error)
    
    info = await message.reply_text("->>> Starting the scraping process...")
    user = message.from_user
    members = []
    
    try:
        last_account = list(userbots.values())[-1]
        await info.edit_text(f"Hold on! We have chosen {last_account} and are now scraping....")
        
        async for member in last_account.get_chat_members(group_id):
            if member.user.is_bot:
                continue
            if member.user.username is None:
                continue
            members.append(member.user.username)
        
        file = backup_member_list(data_list=members)
        try:
            await message.reply_document(file)
        except Exception as err:
            return await info.edit_text(f"Error encountered while sending the document:\n\n{err}")
    except Exception as err:
        return await info.edit_text(err)
    
    return await message.reply_text("Scraping completed.")

@app.on_message(filters.command("load") & filters.user(BOT_OWNER))
async def load_scrape(app, message: Message):
    msg = message.reply_to_message
    if not msg:
        return await message.reply_text("Please reply to a valid member backup file.")
    
    if not msg.document:
        return await message.reply_text("This file is not supported. Please reply to a valid file that ends with .pkl.\n\nTo scrape now, just send this command: /scrape group_username")
    
    info = await message.reply_text("-> Checking the file....")
    try:
        doc = msg.document
        if not doc.file_name.lower().endswith(".pkl"):
            return await message.reply_text("This is not a supported format. Only .pkl files are allowed.")
        
        await info.edit_text("-> File check completed ✅\n\n-> Restoring members...")
        try:
            downloaded = await msg.download()
            nice = restore_member_list(downloaded)
            return await info.edit_text(f"{len(members)} members loaded successfully ✅")
        except Exception as err:
            return await info.edit_text(f"OOPS! An error occurred:\n\n{err}")
    except Exception as err:
        return await info.edit_text(f"OOPS! An error occurred:\n\n{err}\n\n<b>YOU PROBABLY PROVIDED A BROKEN FILE FOR THIS FUNCTION</b>")
