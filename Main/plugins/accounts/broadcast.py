import random
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserDeactivated, UserRestricted, UserPrivacyRestricted

from Main import app, LOGGER
from Main.deco.user_handle import check_user
from Main.database.functions import get_all_userbots, get_subscription as get_user, remove_subscription, add_subscription
from Main.plugins.accounts.scrapper import members
from config import final_msg, last_msg, LOGGER_GROUP

def choose_random_greetings():
    if len(final_msg) == 0:
        return None
    random_words = []
    for inner_list in final_msg:
        random_words.append(random.choice(inner_list))
    return random_words

on_going_broadcast = []

@app.on_message(filters.command("stop"))
async def stop_broadcast(app, msg: Message):
    if msg.from_user.id not in on_going_broadcast:
        return await msg.reply_text("🚫 No broadcast is currently running.")
    try:
        on_going_broadcast.remove(msg.from_user.id)
        return await msg.reply_text("✅ Broadcast has been stopped.")
    except Exception as err:
        return await msg.reply_text("🤔 It seems the broadcast has already been stopped!")

@app.on_message(filters.command("broadcast"))
@check_user
async def broadcast(app, msg: Message):
    user = msg.from_user
    if user.id in on_going_broadcast:
        return await msg.reply_text("🔄 You are already broadcasting. Please wait for the current broadcast to finish or use /stop to cancel it.")
    
    if not members:
        return await msg.reply_text("⚠️ The bot has no members in the list. Please contact the bot owner.")

    split_text = msg.text.lower().split(" ")
    if not msg.reply_to_message:
        return await msg.reply_text("❗ You must reply to a message to broadcast.\n\n**USAGE:** \n/broadcast -> The bot will copy the target message without forwarding.\n/broadcast -forward -> The bot will forward the message to users.")
    
    target_msg = msg.reply_to_message
    resp = await msg.reply_text("📡 Preparing for broadcast...")

    greetings = choose_random_greetings()
    sub_limit = int(await get_user(user.id))

    if sub_limit is None or sub_limit == 0:
        return await resp.edit_text("❌ You don't have any active subscription. Please contact the bot owner to get a subscription.")

    userbots = get_all_userbots()
    if not userbots:
        return await resp.edit_text("⚠️ You don't have any userbots running. Please contact the bot owner.")

    sent = 0
    failed = 0
    used_userbots = 0
    temp_members = members.copy()
    sent_members = []
    
    bcast_msg = await target_msg.forward(LOGGER_GROUP)
    try:
        on_going_broadcast.append(user.id)
        for userbot in userbots:
            if user.id not in on_going_broadcast:
                break
            if sent >= sub_limit:
                await remove_subscription(user.id)
                break

            used_userbots += 1
            try:
                ubot = await userbot.get_me()
                await resp.edit_text(f"📤 Broadcasting in progress...\n\nSending with {ubot.first_name} userbot...")

                for member in list(temp_members):
                    if user.id not in on_going_broadcast:
                        break
                    if sent >= sub_limit:
                        await remove_subscription(user.id)
                        break
                    if member in sent_members:
                        continue
                    try:
                        if greetings:
                            for gmsg in greetings:
                                try:
                                    await userbot.send_message(member, gmsg)
                                    await asyncio.sleep(5)
                                except Exception as err:
                                    LOGGER(f"Error in sending greeting with {ubot.first_name}").error(err)
                                    continue

                        bmsg_id = bcast_msg.id
                        if "-forward" in split_text:
                            try:
                                await userbot.forward_messages(chat_id=member, from_chat_id=str(LOGGER_GROUP), message_ids=bmsg_id)
                            except Exception as err:
                                await userbot.send_message(member, target_msg.text)
                        else:
                            await userbot.copy_message(member, LOGGER_GROUP, bmsg_id)
                        
                        sent += 1
                        sent_members.append(member)
                    except FloodWait as f:
                        await asyncio.sleep(f.value)
                        continue
                    except UserPrivacyRestricted:
                        continue
                    except (UserRestricted, UserDeactivated):
                        continue
                    except Exception as err:
                        failed += 1
                        LOGGER(f"BROADCAST ERROR: ").error(f"Error with {ubot.first_name}. Continuing with the next client.\n{err}")
                        continue
            except Exception as err:
                failed += 1
                LOGGER(f"Error with userbot: ").error(f"Failed to use userbot {ubot.id}/{ubot.first_name}. {err}")
                continue
        
        if len(members) < sub_limit:
            ok = await add_subscription(user.id, abs(sub_limit - len(sent_members)))
            subl = await get_user(user.id)
            await msg.reply_text(f"⚠️ The bot had fewer users than your subscription limit. You have {subl} quota remaining.")

        txt = f"""📊 <b>Broadcast Completed ✅</b>
        <b>Sent:</b> {sent}
        <b>Failed:</b> {failed}
        <b>Clients Used:</b> {used_userbots}
        
        Broadcast executed by {user.mention}. You have used 100% of your quota. Please purchase more quota for additional broadcasts."""
        
        try:
            on_going_broadcast.remove(user.id)
        except:
            pass
        return await resp.edit_text(txt)
    except Exception as err:
        try:
            on_going_broadcast.remove(user.id)
        except:
            pass
        return await resp.edit_text(f"❌ An error occurred: {err}")
