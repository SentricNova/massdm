from pyrogram import Client, idle
from pyrogram.errors import SessionExpired, SessionRevoked, UserAlreadyInvited, UserAlreadyParticipant, UserNotParticipant

from config import LOGGER_GROUP
from Main import app
from Main.database.functions import add_userbot, remove_userbot

async def run_client(api_id, api_hash, session, msg=None):
    try:
        remove_userbot(f"{str(me.first_name)}={str(me.id)}")
    except Exception as err:
        pass
    
    if msg is not None:
        info = await msg.reply_text("🔄 Restarting userbot for standby mode...")

    client = Client(name="MrHelper", api_id=api_id, api_hash=api_hash, session_string=session, in_memory=True)
    
    try:
        await client.start()
        me = await client.get_me()
        add_userbot(f"{str(me.first_name)}={str(me.id)}", client)
        
        try:
            member = await app.get_chat_member(LOGGER_GROUP, me.id)
        except Exception as err:
            link = await app.export_chat_invite_link(LOGGER_GROUP)
            await client.join_chat(link)
        
        if msg is not None:
            await info.edit_text(f"{me.mention} has started and is now in standby mode! 🚀")
        
        try:
            await app.send_message(msg.from_user.id, f"{me.mention} has started successfully! ✅")
        except Exception as err:
            print(err)
            pass
        
        await idle()
        
        if msg is not None:
            await info.edit_text(f"{me.mention} has stopped! ❌")
    
    except KeyboardInterrupt:
        await client.stop()
    
    except (SessionExpired, SessionRevoked):
        if msg is not None:
            await info.edit_text("⚠️ Session has expired! Please generate a new session.")
        return
    
    except Exception as err:
        err_txt = f"**Unexpected error encountered.**\n\n{err}\n\n**SUGGESTIONS:** \nTry generating a new session string. Remember, if you continue using a blocked API ID and hash, your account may remain banned."
        if msg is not None:
            await info.edit_text(err_txt)
        return
    
    finally:
        err_txt = "🛑 Stopping the client..."
        if msg is not None:
            await msg.reply_text(err_txt)
        await client.stop()
    
    return
