import json
import os
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from telethon import TelegramClient, events

from src import DATA_DIR
from src.utils import logger
from src.utils.simple_db import SimpleDB


async def start(bot: TelegramClient):
    userdata = SimpleDB(os.path.join(DATA_DIR, "userdata.json"))

    @bot.on(events.NewMessage(pattern='/start'))
    async def on_start(event):
        for user in userdata.data:
            if user["id"] == event.sender_id:
                logger.debug(f"Not new user: {event.sender_id}")
                break
        else:
            userdata.data.append({"id": event.sender_id, "topics": []})
            userdata.save()
            logger.info(f"New user: {event.sender_id}")
        await event.respond('Hello! Use /help')

    @bot.on(events.NewMessage(pattern='/help'))
    async def on_help(event):
        await event.respond(
            f"**/help** - list of commands\n**/topics** - list of available topics\n**/mytopics** - list of subscribed topics\n**/subscribe <topic>** - subscribe\n**/unsubscribe <topic>** - !subscribe")

    @bot.on(events.NewMessage(pattern='/mytopics'))
    async def on_mytopics(event):
        for user in userdata.data:
            if user["id"] == event.sender_id:
                logger.debug(f"/mytopics from {event.sender_id}: {user['topics']}")
                await event.respond(str(user['topics'] or "No subscribed topics. Use /subscribe <topic>"))
                break
        else:
            logger.warning(f"User {event.sender_id} not in DB!")
            await event.respond('Error!')

    @bot.on(events.NewMessage(pattern='/subscribe (?P<topic>[a-zA-z0-9-]+)'))
    async def on_subscribe(event):
        topic = event.pattern_match.group('topic')
        for user in userdata.data:
            if user["id"] == event.sender_id:
                logger.debug(f"/subscribe {topic} from {event.sender_id}")
                if topic in user["topics"]:
                    await event.respond(f"Already subscribed to {topic} topic!")
                else:
                    user["topics"].append(topic)
                    userdata.save()
                    await event.respond(f"Subscribed to {topic} topic.")
                break
        else:
            logger.warning(f"User {event.sender_id} not in DB!")
            await event.respond('Error!')

    @bot.on(events.NewMessage(pattern='/unsubscribe (?P<topic>[a-zA-z0-9-]+)'))
    async def on_unsubscribe(event):
        topic = event.pattern_match.group('topic')
        for user in userdata.data:
            if user["id"] == event.sender_id:
                logger.debug(f"/subscribe {topic} from {event.sender_id}")
                if topic not in user["topics"]:
                    await event.respond(f"Not subscribed to {topic} topic!")
                else:
                    user["topics"].remove(topic)
                    userdata.save()
                    await event.respond(f"Unsubscribed to {topic} topic.")
                break
        else:
            logger.warning(f"User {event.sender_id} not in DB!")
            await event.respond('Error!')

    consumer = AIOKafkaConsumer('topic',
                                bootstrap_servers=[os.environ.get("KAFKA_HOST")],
                                value_deserializer=lambda m: json.loads(m.decode('utf-8')))
    await consumer.start()
    logger.info(f"Available topics: {await consumer.topics()}")

    @bot.on(events.NewMessage(pattern='/topics'))
    async def on_topics(event):
        await event.respond(f"Available topics: {await consumer.topics()}")

    try:
        async for message in consumer:
            logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                       message.offset, message.key,
                                                       message.value))

            msg = """[{time}] New message in "{chat}":\n{content}""".format(
                time=datetime.fromtimestamp(message.value["timestamp"]),
                chat=message.value["chat_id"],
                content=message.value["message"]
            )

            for user in userdata.data:
                if 'topic' in user["topics"]:
                    logger.debug(f"Sending message to user {user['id']}")
                    await bot.send_message(user["id"], msg)
    finally:
        await consumer.stop()


def main():
    auth = {
        "session": os.path.join(DATA_DIR, "bot"),
        "api_id": int(os.environ.get("API_ID")),
        "api_hash": os.environ.get("API_HASH"),
    }

    with TelegramClient(**auth).start(bot_token=os.environ.get("BOT_TOKEN")) as bot:
        bot.loop.run_until_complete(start(bot))
        bot.run_until_disconnected()


if __name__ == '__main__':
    main()
