from abc import ABC, abstractmethod
from auth import auth_scylla
from datetime import datetime
from fake_useragent import UserAgent
import logging
from logging.handlers import RotatingFileHandler


class BaseScrapper(ABC):
    log_filename = "log.log"

    def __init__(self):
        self.session = auth_scylla()
        self.sleep_time = 9

        self.logger = logging.getLogger(name="base")
        for h in self.logger.handlers:
            self.logger.removeHandler(h)
        self.logger.setLevel(logging.INFO)

        file_handler = RotatingFileHandler(
            self.log_filename, maxBytes=1000000, backupCount=1
        )
        stream_handler = logging.StreamHandler()

        file_handler.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)

        f = logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s [%(pathname)s, %(lineno)d]"
        )

        file_handler.setFormatter(f)
        stream_handler.setFormatter(f)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def log(self, msg, source, level="INFO"):
        if level not in ["INFO", "ERROR", "DEBUG", "CRITICAL"]:
            raise ValueError("Incorrect logging level")

        insert_stmt = """
      INSERT INTO LOGSTORE (msg, level, source, created_ts) VALUES (%s, %s, %s, %s)
      """
        if level == "INFO":
            self.logger.info(msg)
        if level == "ERROR":
            self.logger.exception(msg)
        if level == "DEBUG":
            self.logger.debug(msg)

        # self.session.execute(insert_stmt, [msg, level, source, datetime.now()])

    def get_new_ua(self):
        ua = UserAgent()
        return ua.random

    @abstractmethod
    def collect(self):
        raise NotImplementedError
