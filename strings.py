from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

start_txt = """Hello {0},
I am a bot designed to help you advertise your messages to a wide audience. To learn how to use my features, please click the button below or send the /help command."""

help_txt = """<b>USER COMMANDS:</b>\n\n
/broadcast - When you reply to a user, the message you replied to will be broadcasted to many users.\n\n
/stop - Use this command to stop an ongoing broadcast.\n\n
BROADCAST OPTIONS:\n
`-forward` - Add this option to the broadcast command if you want to forward a message. If you do not include it, the message will be copied and sent to the users."""

start_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("❓ Help Menu", callback_data="open_help")],
        [InlineKeyboardButton("🛒 Buy Subscription", callback_data="buy_subscription")],
        [InlineKeyboardButton("📊 Check Balance/Usage", callback_data="check_usage")]
    ]
)

help_keyboard = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🏠 Go to Home", callback_data="open_home")]
    ]
)

