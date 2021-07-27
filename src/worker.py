import asyncio
import json
import os
from typing import Dict, List

from aiokafka import AIOKafkaProducer
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel

from src.utils import logger


class TelegramWorker:
    def __init__(self, client: TelegramClient, bootstrap_servers: str, chats_to_listen: List[str] = None):
        self.bootstrap_servers = bootstrap_servers
        self.client = client
        self.chats_to_listen = chats_to_listen or ['me']

    async def send(self, data: Dict):
        data["from"] = "telegram-worker"
        j = json.dumps(data)
        logger.debug(f"Sending message to Kafka: {j}")
        await self.producer.send_and_wait('topic', j.encode('utf-8'))

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()
        await self.client.start()

        for chat in self.chats_to_listen:
            try:
                channel = await self.client.get_entity(chat)
                if not isinstance(channel, Channel):
                    logger.warning(f"Chat {chat} is not channel, skipping...")
                    continue

                # TODO: ignore already joined
                await self.client(JoinChannelRequest(channel))
                logger.info(f"Joined to {channel}")
            except Exception:
                logger.warning(f"Error while trying join to chat {chat}")

        @self.client.on(events.NewMessage(chats=self.chats_to_listen))
        async def handler(event):
            logger.info(event.message)

            message_data = {
                "chat_id": event.chat_id,
                "sender_id": event.sender_id,
                "message_id": event.message.id,
                "timestamp": event.message.date.timestamp(),
                "message": event.message.message,
            }

            await self.send(message_data)

        return self

    async def stop(self, *args):
        await self.producer.stop()
        await self.client.disconnect()

    __aenter__ = start
    __aexit__ = stop

    def __enter__(self):
        return self.client.loop.run_until_complete(self.__aenter__())

    def __exit__(self, *args):
        self.client.loop.run_until_complete(self.__aexit__(*args))

    async def run(self):
        await self.client.run_until_disconnected()

    # def run(self):
    #     with TelegramClient(
    #             session=StringSession(os.environ.get("STRING_SESSION")),
    #             api_id=int(os.environ.get("API_ID")),
    #             api_hash=os.environ.get("API_HASH"),
    #     ) as self.client:
    #         self.client.loop.run_until_complete(self.start())
    #         self.client.run_until_disconnected()
    #     # try:
    #     #     self.client.loop.run_until_complete(self.start())
    #     #     self.client.run_until_disconnected()
    #     # finally:
    #     #     self.stop()


def main():
    client = TelegramClient(
        session=StringSession(os.environ.get("STRING_SESSION")),
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
    )

    with TelegramWorker(client, os.environ.get("KAFKA_HOST")) as worker1:
    # with worker1.client:
    #     worker1.client.loop.run_until_complete(worker1.start())
    #     worker1.client.run_until_disconnected()
    # worker1.client.loop.run_until_complete(worker1.start())
        async def main_loop():
            while True:
                await worker1.client.run_until_disconnected()

        loop = asyncio.get_event_loop()
        loop.create_task(main_loop())
        loop.run_forever()


if __name__ == '__main__':
    main()
