#!/usr/bin/python3


import json
import logging
import os

from telethon.sync import TelegramClient, events

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger('telegram-worker')
logger.setLevel(logging.DEBUG)


def send_message_data(message_data):
    OUTPUT_FILENAME = "output.json"
    if os.path.exists(OUTPUT_FILENAME):
        with open(OUTPUT_FILENAME, "r", encoding="utf-8") as f:
            messages = json.load(f)
    else:
        messages = []

    messages.append(message_data)

    with open("output.json", "w", encoding="utf-8") as output:
        json.dump(messages, output, indent=4)


async def main():
    logger.info("Started")

    CHATS_TO_LISTEN = [
        "me",
        "telegram",
        "RBCCrypto",
        "breakingmash",
    ]

    @client.on(events.NewMessage(chats=CHATS_TO_LISTEN))
    async def handler(event):
        logger.info(event.message)

        message_data = {
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "message_id": event.message.id,
            "timestamp": event.message.date.timestamp(),
            "message": event.message.message,
        }

        send_message_data(message_data)


if __name__ == '__main__':
    if bool(os.environ.get('DEBUG', True)):
        logger.debug("Authentication from auth.json")
        with open("auth.json", "r") as f:  # {"api_id": {{}},"api_hash": "{{}}","bot_token": "{{}}"}
            auth = json.load(f)
    else:
        logger.debug("Authentication from env values")
        auth = {
            "api_id": int(os.environ.get("API_ID", 'wrong-ip')),
            "api_hash": os.environ.get("API_HASH", 'wrong-hash'),
            "bot_token": os.environ.get("BOT_TOKEN", 'wrong-bot-token'),
        }

    name = "bot"
    api_id = auth["api_id"]
    api_hash = auth["api_hash"]

    client = TelegramClient(name, api_id, api_hash)

    if "bot_token" in auth:
        logger.info("Using BOT TOKEN")
        client = client.start(bot_token=auth["bot_token"])

    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()
