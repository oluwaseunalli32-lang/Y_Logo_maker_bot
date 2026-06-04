import os
import logging
import asyncio
import httpx
import urllib.parse
import random
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
        "🎨 <b>Creating your custom logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # 2. Frame a strict, optimized prompt for actual graphics generation
        clean_text = user_text.replace("/", " ").replace("?", " ").replace("&", "and")
        logo_prompt = f"professional minimalist vector logo design for {clean_text}, clean geometric lines, modern branding icon, white background, high resolution digital graphic"
        
        # Safely URL encode the prompt text
        encoded_prompt = urllib.parse.quote(logo_prompt)
        seed = random.randint(1, 999999)
        
        # Using a verified unauthenticated public AI rendering pipe mirror
        image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&nofeed=true"

        # 3. Download the graphic using httpx (60-second timeout window)
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(image_url)
            
            if response.status_code == 200 and len(response.content) > 5000:
                # 4. Send the real generated design back to the user
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your unique logo concept for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"API returned status code: {response.status_code}")
                await status_message.edit_text(f"❌ Generation took too long or was restricted. Please try a slightly shorter description!")

    except Exception as e:
        logger.exception("Error generating logo details:") 
        await status_message.edit_text("⚠️ An error occurred while rendering your design. Please try again.")

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

    logger.info("Starting bot pipeline with verified rendering mirrors...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
