import asyncio
import os

from telethon import TelegramClient
from telethon.sessions import StringSession

from src import DATA_DIR
from src.consumer import start
from src.worker import TelegramWorker


def main():
    auth = {
        "api_id": int(os.environ.get("API_ID")),
        "api_hash": os.environ.get("API_HASH"),
    }

    client = TelegramClient(
        session=StringSession(os.environ.get("STRING_SESSION")),
        **auth
    )

    chats_to_listen = [
        'me',
        "breakingmash",
        "meduzalive",
        "moscowmap",
        "moscowach",
        "corona",
        "COVID2019_official",

        "RBCCrypto",
        "buff_10",
        "DeCenter",
        "crypto_sekta",
        "SIGEN_Media",
        "ForkLog",
        "MinterNetwork",
        "Proffit_crypto",
        "Kriptamoney",
        "incrypted",
        "ico_analytic",
        "crypto_forest",
        "Pro_Blockchain",
        "Rosenthal_signal",
        "crypto_hike",
    ]

    with TelegramWorker(client, os.environ.get("KAFKA_HOST"), chats_to_listen) as worker, \
            TelegramClient(session=os.path.join(DATA_DIR, "bot"), **auth).start(
                bot_token=os.environ.get("BOT_TOKEN")) as bot:
        bot.loop.run_until_complete(start(bot))

        async def main_loop():
            while True:
                await worker.run()
                await bot.run_until_disconnected()

        loop = asyncio.get_event_loop()
        loop.create_task(main_loop())
        loop.run_forever()


if __name__ == '__main__':
    main()
