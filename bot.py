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
        "🎨 <b>Creating your custom logo design...</b> Please wait a few seconds.", 
        parse_mode="HTML"
    )

    try:
        # 2. Build a high-quality logo vector prompt layout
        clean_text = user_text.replace("/", " ").replace("?", " ").replace("&", "and")
        logo_prompt = f"professional minimalist vector logo design for {clean_text}, flat 2d graphic layout, clean geometric lines, white background, high contrast, modern icon"
        
        # 3. Use Hugging Face's open-access PixArt inference API (No API keys or signup required)
        api_url = "https://api-inference.huggingface.co/models/PixArt-alpha/PixArt-XL-2-1024-MS"
        
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": logo_prompt,
            "options": {"wait_for_model": True}
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            
            # Verify we received a valid image byte stream back
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
                await status_message.edit_text("❌ The generation server is currently cycling. Please wait a moment and try again!")

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

    logger.info("Starting bot pipeline with open Hugging Face API layers...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
