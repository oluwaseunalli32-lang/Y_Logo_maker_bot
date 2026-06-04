import os
import logging
import asyncio
import httpx
import random
import urllib.parse
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
    """Handle incoming user text descriptions, generate a logo, and send it."""
    user_text = update.message.text
    chat_id = update.effective_chat.id

    # 1. Show typing status
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    
    status_message = await update.message.reply_text(
        "🎨 <b>Creating your logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # 2. Build a high-quality logo prompt structure
        logo_prompt = (
            f"professional minimalist vector logo design for {user_text}, "
            f"clean geometric lines, modern branding icon, white background, high resolution"
        )
        encoded_prompt = urllib.parse.quote(logo_prompt)
        seed = random.randint(1, 99999)

        # 3. Use an alternative open engine to bypass limits completely
        # This endpoint delivers high-speed vector-style prints for free
        api_url = f"https://image.prodia.com/generate?prompt={encoded_prompt}&model=AbsoluteReality_v1.8.1.safetensors&seed={seed}&width=1024&height=1024"

        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.get(api_url)
            
            if response.status_code == 200:
                # 4. Return image bytes straight to the client window
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your logo for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"Engine returned error code: {response.status_code}")
                await status_message.edit_text(f"❌ Server busy (Status: {response.status_code}). Please try again in a moment!")

    except Exception as e:
        logger.exception("Error during core image creation sequence:") 
        await status_message.edit_text("⚠️ An unexpected error occurred. Please try a different description.")

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

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting up with open generation processing framework...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
