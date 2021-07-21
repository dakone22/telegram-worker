import json
import os

from telethon.sync import TelegramClient, events


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
    print("Started")

    CHATS_TO_LISTEN = [
        "me",
        "telegram",
        "RBCCrypto",
        "breakingmash",
    ]

    @client.on(events.NewMessage(chats=CHATS_TO_LISTEN))
    async def handler(event):
        print(event.message)

        message_data = {
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "message_id": event.message.id,
            "timestamp": event.message.date.timestamp(),
            "message": event.message.message,
        }

        send_message_data(message_data)


if __name__ == '__main__':
    with open("auth.json", "r") as f:
        auth = json.load(f)

    name = "session_name"
    api_id = auth["api_id"]
    api_hash = auth["api_hash"]

    client = TelegramClient(name, api_id, api_hash)

    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()
