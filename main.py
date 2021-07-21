import json
from telethon.sync import TelegramClient, events

with open("auth.json", "r") as f:
    auth = json.load(f)

api_id = auth["api_id"]
api_hash = auth["api_hash"]

with TelegramClient('session_name', api_id, api_hash) as client:
    client.send_message('me', 'Hello, myself!')
    print(client.download_profile_photo('me'))

    @client.on(events.NewMessage(pattern='(?i).*Hello'))
    async def handler(event):
        await event.reply('Hey!')

    client.run_until_disconnected()
