# Telegram Webhook Bot

A Telegram bot that forwards received messages to a specified webhook URL, built with Flask and deployable to Vercel.

## Features

- Forwards all text messages received by the bot to a specified webhook URL
- Provides immediate feedback to users about message forwarding status
- Includes message metadata in the forwarded payload
- Deployable to Vercel as a serverless function

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

## Deployment to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy to Vercel:
```bash
vercel
```

3. After deployment, set your environment variables in Vercel:
   - Go to your project settings in Vercel dashboard
   - Add `TELEGRAM_TOKEN` and `WEBHOOK_URL` environment variables

4. Set up Telegram Webhook:
   Replace `YOUR_VERCEL_URL` with your deployed URL:
```bash
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook?url=YOUR_VERCEL_URL/api/webhook"
```

## Webhook Payload Format

The webhook will receive POST requests with JSON payloads in this format:
```json
{
    "message_id": 123,
    "chat_id": 456,
    "text": "Message content",
    "date": 1234567890,
    "from_user": {
        "id": 789,
        "username": "sender_username",
        "first_name": "First",
        "last_name": "Last"
    }
}
```

## Development

To run locally:
```bash
flask run
```

Then use ngrok or similar to create a tunnel to your local server for testing:
```bash
ngrok http 5000
```

## Error Handling

The bot includes comprehensive error handling:
- Validates message format
- Handles network timeouts
- Provides user-friendly error messages
- Maintains detailed logs
- Never crashes on malformed messages
