import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward the received message to the webhook URL."""
    try:
        # Validate that we have a message object
        if not update.message:
            logger.warning("Received update without message object")
            return

        # Extract message content
        message = update.message
        
        # Validate message has text content
        if not message.text:
            await message.reply_text("❌ Sorry, I can only process text messages.")
            logger.warning(f"Received message {message.message_id} without text content")
            return

        # Validate sender information
        if not message.from_user:
            await message.reply_text("❌ Error: Could not identify message sender.")
            logger.warning(f"Message {message.message_id} has no sender information")
            return
            
        # Prepare payload with safe getters to avoid AttributeError
        payload = {
            'message_id': message.message_id,
            'chat_id': message.chat_id,
            'text': message.text,
            'date': message.date.isoformat() if message.date else None,
            'from_user': {
                'id': message.from_user.id,
                'username': getattr(message.from_user, 'username', None),
                'first_name': getattr(message.from_user, 'first_name', None),
                'last_name': getattr(message.from_user, 'last_name', None)
            }
        }
        
        try:
            # Send POST request to webhook with timeout
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Message {message.message_id} forwarded successfully to webhook. Status code: {response.status_code}")
            
            # Send success reply
            await message.reply_text("✅ Message successfully forwarded!")
            
        except requests.exceptions.Timeout:
            logger.error(f"Webhook request timed out for message {message.message_id}")
            await message.reply_text("❌ Request timed out while forwarding your message. Please try again later.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to forward message {message.message_id} to webhook: {str(e)}")
            await message.reply_text("❌ Failed to forward your message. Please try again later.")
            
    except AttributeError as e:
        logger.error(f"Invalid message format or missing attributes: {str(e)}")
        await message.reply_text("❌ Error processing your message format.")
    except ValueError as e:
        logger.error(f"Error processing message values: {str(e)}")
        await message.reply_text("❌ Error processing your message data.")
    except Exception as e:
        logger.error(f"Unexpected error while processing message: {str(e)}")
        logger.exception("Full traceback:")
        await message.reply_text("❌ An unexpected error occurred while processing your message.")
    
    # Log that we're still alive and ready for next message
    logger.debug("Handler completed, ready for next message")

def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        logger.error("Telegram token not found in environment variables!")
        return
    if not WEBHOOK_URL:
        logger.error("Webhook URL not found in environment variables!")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
