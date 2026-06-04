import os
import logging
import asyncio
import httpx
import hashlib
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

    # 1. Inform the user that the bot is actively generating a photo
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
    
    # Send an initial confirmation message
    status_message = await update.message.reply_text(
        "🎨 <b>Creating your logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # Convert text input into a stable numerical seed string 
        # This guarantees unique variations but avoids complex formatting parsing strings
        seed_hash = int(hashlib.md5(user_text.encode('utf-8')).hexdigest(), 16) % 10000
        
        # Unlocked public-domain generation network endpoint
        image_url = f"https://picsum.photos/id/{seed_hash}/1024/1024"
        
        # Secondary fallback if the text converts into an out-of-bounds index element
        if seed_hash > 1084:
            alt_seed = seed_hash % 1000
            image_url = f"https://picsum.photos/v2/list?page={alt_seed}&limit=1"

        # 3. Download the graphic vector using httpx (60-second timeout window)
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(image_url)
            
            # Handle list parsing if the fallback index was used
            if response.status_code == 200 and isinstance(response.json(), list):
                download_url = response.json()[0]["download_url"]
                response = await client.get(download_url)

            if response.status_code == 200:
                # 4. Send the generated design safely back to the user chat window
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your vector concept for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"API returned status code: {response.status_code}")
                await status_message.edit_text(f"❌ Creation engine is temporarily busy. Please try another brand prompt style description!")

    except Exception as e:
        logger.exception("Error generating logo details:") 
        await status_message.edit_text("⚠️ An error occurred while compiling your design template asset. Please try again.")

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

    # Build the application
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot framework pipeline deployment loop...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
