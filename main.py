#!/usr/bin/python3


import json
import logging
import os

from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger('telegram-worker')
logger.setLevel(logging.DEBUG)

DEBUG = bool(os.environ.get('DEBUG', True))

if DEBUG:
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
else:
    from kafka import KafkaProducer

    producer = KafkaProducer(security_protocol="SSL", bootstrap_servers=os.environ.get("KAFKA_HOST"))


    def send_message_data(message_data):
        j = json.dumps(message_data)
        logger.debug(f"Sending message to Kafka: {j}")
        producer.send(j)


async def main(client):
    logger.info("Started")

    CHATS_TO_LISTEN = [
        "me",
        "telegram",
        "RBCCrypto",
        "breakingmash",
    ]

    for chat in CHATS_TO_LISTEN:
        try:
            channel = await client.get_entity(chat)
            if not isinstance(channel, Channel):
                logger.info(f"{chat} is not channel, skipping...")
                continue

            await client(JoinChannelRequest(channel))
            logger.info(f"Joined to {channel}")
        except Exception:
            logger.warning(f"Error while trying join to chat {chat}")

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
    if DEBUG:
        logger.debug("Authentication from auth.json")
        with open("auth.json", "r") as f:  # {"api_id": {{}},"api_hash": "{{}}","bot_token": "{{}}"}
            auth = json.load(f)
    else:
        logger.debug("Authentication from env values")
        has_string_session = "STRING_SESSION" in os.environ
        auth = {
            "api_id": int(os.environ.get("API_ID", 'wrong-ip')),
            "api_hash": os.environ.get("API_HASH", 'wrong-hash'),
        }

    name = "worker"
    api_id = auth["api_id"]
    api_hash = auth["api_hash"]

    client = TelegramClient(StringSession(os.environ.get("STRING_SESSION")) if has_string_session else StringSession(), api_id, api_hash)

    with client:
        if DEBUG: logger.debug(client.session.save())
        client.loop.run_until_complete(main(client))
        client.run_until_disconnected()
