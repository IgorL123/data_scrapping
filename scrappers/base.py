from abc import ABC, abstractmethod
from auth import auth_scylla
from datetime import datetime
from fake_useragent import UserAgent


class BaseScrapper(ABC):

   def __init__(self):
      self.session = auth_scylla()

   def log(self, msg, source, level="INFO"):

      if level not in ["INFO", "ERROR", "DEBUG", "CRITICAL"]:
         raise ValueError("Incorrect logging level")
      
      insert_stmt = """
      INSERT INTO LOGSTORE (msg, level, source, created_ts) VALUES (%s, %s, %s, %s)
      """
      self.session.execute(insert_stmt, [msg, level, source, datetime.now()])
   

   def get_new_ua(self):
      ua = UserAgent()
      return ua.random

   @abstractmethod
   def collect(self):
      raise NotImplementedError
