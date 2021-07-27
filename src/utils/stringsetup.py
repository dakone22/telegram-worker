import os

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print(
    "Please go-to my.telegram.org",
    "Login using your Telegram account",
    "Click on API Development Tools",
    "Create a new application, by entering the required details",
    sep='\n'
)

api_id = int(os.environ.get("API_ID") or input("Enter APP ID here: "))
api_hash = os.environ.get("API_HASH") or input("Enter API HASH here: ")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
    client.send_message("me", client.session.save())
