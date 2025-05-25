import asyncio
from pyrogram import idle
from Main import LOGGER, app


async def init():
    await app.start()
    LOGGER("BOOT >>").info(f"Bot {app.name} has started successfully.")
    
    await idle()  # Keep the client idle to listen for updates
    await app.stop()
    LOGGER("SHUTDOWN >>").info(f"Bot {app.name} is shutting down.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
