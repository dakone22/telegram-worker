import json
import os.path

from src.utils import logger


class SimpleDB:
    def __init__(self, location):
        self.data = None
        self.location = os.path.abspath(location)

        self.load(self.location)

    @classmethod
    def _get_default_value(cls):
        return list()

    def load(self, location):
        if not os.path.exists(location):
            self.data = SimpleDB._get_default_value()
        else:
            with open(self.location, "r") as fs:
                try:
                    self.data = json.load(fs)
                except json.decoder.JSONDecodeError as e:
                    logger.critical(f"Load Error : {e}")
                    return False
        return True

    def save(self):
        with open(self.location, "w+") as fs:
            try:
                json.dump(self.data, fs)
            except TypeError as e:
                logger.critical(f"Save Error : {e}")
                return False

        return True

    def reset(self):
        self.data = SimpleDB._get_default_value()
        self.save()
        return True
