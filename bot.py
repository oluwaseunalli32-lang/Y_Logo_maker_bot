import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    # Using HTML tags ensures underscores in Y_Logo_maker_bot don't break the parser
    welcome_text = (
        f"🤖 <b>Welcome to Y_Logo_maker_bot, {user.first_name}!</b>\n\n"
        "Need a professional logo in seconds? Describe your brand, "
        "and let powerful AI handle the rest.\n\n"
        "👉 Type your brand name and style preference to begin!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just send me your brand name and design preferences!")

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    # Set up a fresh event loop explicitly to fix Python 3.14+ MainThread error
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot using long polling
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
