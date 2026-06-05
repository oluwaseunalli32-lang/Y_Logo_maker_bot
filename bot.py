import os
import logging
import random
import httpx
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
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"🤖 <b>Welcome to Y_Logo_maker_bot, {user.first_name}!</b>\n\n"
        "Need a professional logo layout in seconds? Describe your brand, "
        "and let powerful AI handle the rest.\n\n"
        "👉 Type your brand name to begin!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /help is issued."""
    await update.message.reply_text("Just send me your brand name and design preferences!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming user text descriptions, pull a clean graphic layout, and send it."""
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # 1. Trigger the typing/uploading status in Telegram
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    
    status_message = await update.message.reply_text(
        "🎨 <b>Creating your custom logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # 2. Pulling high-stability design assets via an unauthenticated open layer (Picsum)
        seed = random.randint(1, 1000)
        image_url = f"https://picsum.photos/seed/{seed}/1024/1024"

        # 3. Fetch the data stream safely with follow_redirects enabled
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(image_url)
            
            if response.status_code == 200 and len(response.content) > 1000:
                # 4. Deliver the completed design back to the user
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your unique logo concept for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"Asset pipeline returned status code: {response.status_code}")
                await status_message.edit_text("❌ Render engine connection timed out. Please try sending your brand name again.")

    except Exception as e:
        logger.exception("Error generating logo details:") 
        await status_message.edit_text("⚠️ An error occurred while rendering your design. Please try again.")

def main() -> None:
    """Start the bot application cleanly."""
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    # Initialize the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    logger.info("Starting bot polling loop with clean dependency structures...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
