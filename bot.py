import os
import logging
import asyncio
import httpx
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
        "🎨 <b>Creating your logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # 2. Sanitize user text strictly to match legacy Pollinations CDN path requirements
        # Strip out symbols that trigger the 400 Bad Request firewall
        clean_text = user_text.replace(",", " ").replace(".", " ").replace("/", " ").replace("?", " ").replace("-", " ")
        
        # Combine into an optimized logo prompt layout
        prompt_string = f"professional minimalist vector logo design for {clean_text} clean geometric lines modern branding icon white background"
        
        # FIX: Pollinations open CDN requires spaces to be underscores (_) to prevent pathing breaks
        formatted_prompt = "_".join(prompt_string.split())
        
        # Add a random seed to the end of the path string to force a unique image generation
        seed = random.randint(1, 999999)
        
        # The ultimate open-access endpoint route
        image_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}_{seed}"

        # 3. Download the image using httpx (60-second timeout window)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(image_url)
            
            if response.status_code == 200:
                # 4. Send the generated image directly to the user
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=response.content,
                    caption=f"✅ <b>Here is your logo for:</b>\n<i>\"{user_text}\"</i>",
                    parse_mode="HTML"
                )
                await status_message.delete()
            else:
                logger.error(f"API returned status code: {response.status_code}")
                await status_message.edit_text(f"❌ Generation failed (Status: {response.status_code}). Please try a different description!")

    except Exception as e:
        logger.exception("Error generating logo details:") 
        await status_message.edit_text("⚠️ An error occurred while generating your logo. Please try again.")

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

    logger.info("Starting bot polling with free-tier CDN generation...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
