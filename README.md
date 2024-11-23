# Telegram Webhook Bot

A simple Telegram bot that forwards received messages to a specified webhook URL.

## Setup

1. Create a new Telegram bot by talking to [@BotFather](https://t.me/botfather) and get your bot token

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

4. Edit the `.env` file and add your:
   - Telegram bot token
   - Webhook URL where messages should be forwarded

## Running the Bot

Simply run:
```bash
python bot.py
```

## Features

- Forwards all text messages received by the bot to a specified webhook URL
- Includes message metadata in the forwarded payload:
  - Message ID
  - Chat ID
  - Message text
  - Timestamp
  - Sender information (ID, username, first name, last name)
- Logging of successful forwards and errors

## Webhook Payload Format

The webhook will receive POST requests with JSON payloads in this format:
```json
{
    "message_id": 123,
    "chat_id": 456,
    "text": "Message content",
    "date": "2023-01-01T12:00:00+00:00",
    "from_user": {
        "id": 789,
        "username": "sender_username",
        "first_name": "First",
        "last_name": "Last"
    }
}
```
