import os
import json
import logging
import requests
from flask import Flask, request, Response
from dotenv import load_dotenv

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

app = Flask(__name__)

def send_telegram_message(chat_id, text):
    """Helper function to send Telegram messages."""
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        logger.info(f"Sending Telegram message to {chat_id}: {text}")
        response = requests.post(
            telegram_url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
        response.raise_for_status()
        logger.info(f"Successfully sent Telegram message: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")
        return False

@app.route('/')
def home():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return {"status": "ok", "telegram_token_set": bool(TELEGRAM_TOKEN), "webhook_url_set": bool(WEBHOOK_URL)}

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates."""
    logger.info("Received webhook call")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    try:
        # Log raw request data
        raw_data = request.get_data().decode('utf-8')
        logger.info(f"Raw request data: {raw_data}")
        
        update = request.get_json()
        logger.info(f"Parsed update data: {json.dumps(update, indent=2)}")
        
        # Validate update has message
        if not update or 'message' not in update:
            logger.warning("Received update without message")
            return Response(status=200)

        message = update['message']
        
        # Validate message has text
        if 'text' not in message:
            chat_id = message.get('chat', {}).get('id')
            if chat_id:
                send_telegram_message(chat_id, "❌ Sorry, I can only process text messages.")
            logger.warning(f"Received message without text content")
            return Response(status=200)

        # Extract necessary information
        chat_id = message['chat']['id']
        text = message['text']
        user = message.get('from', {})
        
        # Prepare payload
        payload = {
            'message_id': message.get('message_id'),
            'chat_id': chat_id,
            'text': text,
            'date': message.get('date'),
            'from_user': {
                'id': user.get('id'),
                'username': user.get('username'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name')
            }
        }

        try:
            # Forward to webhook
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            # Send success message
            send_telegram_message(chat_id, "✅ Message successfully forwarded!")
            logger.info(f"Message forwarded successfully to webhook. Status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            logger.error("Webhook request timed out")
            send_telegram_message(
                chat_id,
                "❌ Request timed out while forwarding your message. Please try again later."
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to forward to webhook: {str(e)}")
            send_telegram_message(
                chat_id,
                "❌ Failed to forward your message. Please try again later."
            )
            
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        logger.exception("Full traceback:")
        # Try to notify user if we can get chat_id
        try:
            chat_id = update.get('message', {}).get('chat', {}).get('id')
            if chat_id:
                send_telegram_message(
                    chat_id,
                    "❌ An unexpected error occurred while processing your message."
                )
        except:
            pass
    
    # Always return 200 to Telegram
    return Response(status=200)

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify the bot can send messages."""
    try:
        if not TELEGRAM_TOKEN:
            return {"error": "TELEGRAM_TOKEN not set"}, 400
            
        # Get chat_id from query parameter
        chat_id = request.args.get('chat_id')
        if not chat_id:
            return {"error": "chat_id parameter required"}, 400
            
        # Try to send a test message
        success = send_telegram_message(chat_id, "🔄 Test message from bot")
        
        return {
            "success": success,
            "message": "Test message sent" if success else "Failed to send test message"
        }
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run()
