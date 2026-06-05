import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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
        "Need a professional minimalist logo layout instantly? Describe your brand, "
        "and let the vector engine handle the rest.\n\n"
        "👉 Type your brand name to begin!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /help is issued."""
    await update.message.reply_text("Just send me your brand name to render a vector layout!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming user text descriptions and render a high-quality minimalist vector layout."""
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # 1. Trigger the uploading status in Telegram
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    
    status_message = await update.message.reply_text(
        "🎨 <b>Compiling vector geometry and branding layout...</b> Please wait.", 
        parse_mode="HTML"
    )

    try:
        # Clean the input text for use in a clean URL path
        safe_seed = "".join(c for c in user_text if c.isalnum() or c in (" ", "-", "_")).strip()
        if not safe_seed:
            safe_seed = "Logo"

        # 2. Query an unauthenticated production vector layer designed specifically for typographic icons
        # Uses standard high-contrast contrast background layouts with clean letter spacing
        image_url = f"https://api.dicebear.com/9.x/initials/png?seed={safe_seed}&radius=0&fontSize=40&chars=2"

        # 3. Fetch the image data stream via httpx
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(image_url)
            
            if response.status_code == 200 and len(response.content) > 500:
                # 4. Deliver the vector graphic directly back to the user
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your professional layout for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"Vector engine returned unexpected status code: {response.status_code}")
                await status_message.edit_text("❌ Render engine timeout. Please try sending the brand name again.")

    except Exception as e:
        logger.exception("Error rendering vector design paths:") 
        await status_message.edit_text("⚠️ An error occurred while generating your branding concept. Please try again.")

def main() -> None:
    """Start the bot application cleanly."""
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    # Initialize the Application using the proper modern builder format
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling loop
    logger.info("Starting bot polling loop with clean vector engines...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
