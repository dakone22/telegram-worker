import logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("telegram-worker")
logger.setLevel(logging.DEBUG)
