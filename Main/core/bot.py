import config
from Main import LOGGER

# Attempt to import and install the uvloop library for potentially faster event loop.
try:
    import uvloop # type: ignore
    uvloop.install()
except ImportError as e:
    LOGGER(__name__).warning(f"uvloop is not installed. Running without it. Details: {e}")
except Exception as e:
    LOGGER(__name__).error(f"Error installing uvloop: {e}")

# Import necessary modules and classes from the Pyrogram library.
from pyrogram import Client, errors
from pyrogram.types import BotCommand
from pyrogram.enums import ChatMemberStatus, ParseMode



plugins = dict(root="Main/plugins")

class botClient(Client):
    def __init__(self):
        """
        Initializes the bot client with necessary parameters.
        """
        LOGGER(__name__).info(f"Starting the bot...")
        super().__init__(
            name="orypbot",  # A unique name for the client session.
            api_id=config.API_ID,  # Your Telegram API ID.
            api_hash=config.API_HASH,  # Your Telegram API HASH.
            bot_token=config.BOT_TOKEN,  # The token of your Telegram bot.
            in_memory=True,  # Run the client session in memory.
            parse_mode=ParseMode.HTML,  # Default parse mode for messages sent by the bot.
            max_concurrent_transmissions=7,  # Maximum number of concurrent outgoing calls.
            plugins=plugins,  # Load plugins from the specified directory.
        )

    async def start(self):
        """
        Starts the bot client and initializes bot-related information.
        """
        await super().start()
        self.id = self.me.id
        self.name = f"{self.me.first_name} {self.me.last_name or ''}".strip()
        self.username = self.me.username
        self.mention = self.me.mention
        
        if config.LOGGER_GROUP:
            try:
                await self.send_message(
                    chat_id=config.LOGGER_GROUP,
                    text=(
                        f"<u>» <b>{self.mention}</b> Bot Started :</u>\n\n"
                        f"ID: <code>{self.id}</code>\n"
                        f"Name: {self.name}\n"
                        f"Username: @{self.username}"
                    ),
                )
            except (errors.ChannelInvalid, errors.PeerIdInvalid):
                LOGGER(__name__).error("Bot failed to access the log group/channel. Please ensure the configured LOG_GROUP ID is correct and the bot is added to the group/channel.")
                raise RuntimeError("Log group/channel access failure.")
            except Exception as err:
                LOGGER(__name__).error(f"An unexpected error occurred while trying to access the log group/channel: {type(err).__name__}.")
                raise

            try:
                member = await self.get_chat_member(config.LOGGER_GROUP, self.id)
                if member.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("The bot is not an administrator in the configured logger group.")
                    raise RuntimeError("Bot is not an admin in the log group/channel.")
            except errors.PeerIdInvalid:
                LOGGER(__name__).error("The configured LOG_GROUP ID is invalid. Please check your configuration.")
                raise RuntimeError("Invalid log group/channel ID.")
            except errors.ChatAdminRequired:
                LOGGER(__name__).error("Admin rights are required to check bot's status in the log group/channel.")
                raise RuntimeError("Admin rights required in log group/channel.")
            except Exception as e:
                LOGGER(__name__).error(f"An error occurred while checking admin status in the log group/channel: {e}")
                raise
        try:
            await self.set_bot_commands([
                BotCommand("start", "Start the bot"),
                BotCommand("help", "Open help menu"),
                BotCommand("load", "Load members from .pkl file"),
                BotCommand("broadcast", "Broadcast to the users")])
        except Exception as err:
            LOGGER(__name__).error(str(err))
        LOGGER(__name__).info(f"Bot Started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Bot...")
        await super().stop()