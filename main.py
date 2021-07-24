#!/usr/bin/python3


import json
import logging
import os

from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel

from kafka import KafkaProducer

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger('telegram-worker')
logger.setLevel(logging.DEBUG)

producer = KafkaProducer(bootstrap_servers=os.environ.get("KAFKA_HOST"))


def send_message_data(message_data):
    j = json.dumps(message_data)
    logger.debug(f"Sending message to Kafka: {j}")
    producer.send('topic', j.encode('utf-8'))


async def start(client):
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
                logger.warning(f"Chat {chat} is not channel, skipping...")
                continue

            # TODO: ignore already joined
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


def main():
    auth = {
        "session": StringSession(os.environ.get("STRING_SESSION")),
        "api_id": int(os.environ.get("API_ID")),
        "api_hash": os.environ.get("API_HASH"),
    }

    with TelegramClient(**auth) as client:
        client.loop.run_until_complete(start(client))
        client.run_until_disconnected()


if __name__ == '__main__':
    main()
