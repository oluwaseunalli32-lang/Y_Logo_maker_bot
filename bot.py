import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming user text descriptions for logos."""
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # 1. Show a 'Visual Status' so the user knows the bot is working
    # Since we aren't generating a real image yet, we'll use "TYPING"
    # Once you connect an image API later, change ChatAction.TYPING to ChatAction.UPLOAD_PHOTO
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    # Simulate a tiny delay for realism
    await asyncio.sleep(1.5)

    # 2. Reply acknowledging their prompt
    response_text = (
        f"🎨 <b>Got it!</b> Analyzing your brand request:\n"
        f"<i>\"{user_text}\"</i>\n\n"
        f"⏳ Image generation pipeline blueprint is ready! (Connect your AI generation API here next)."
    )
    await update.message.reply_text(response_text, parse_mode="HTML")

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = Application.builder().token(TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Message Handler - This listens to all text messages that AREN'T commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot polling with message handler...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
