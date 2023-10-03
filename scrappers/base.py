from auth import auth_scylla
from datetime import datetime
import logging


class BaseScrapper:

   def __init__(self):
      
      self.session = auth_scylla

   def collect(self):
      pass

   def __log(self, msg, source, level="INFO"):

      if level not in ["INFO", "ERROR", "DEBUG", "CRITICAL"]:
         raise ValueError("Incorrect logging level")
      
      insert_stmt = """
      INSERT INTO LOGSTORE (msg, level, source, created_ts) VALUES (%s, %s, %s, %s)
      """
      self.session.execute(insert_stmt, [msg, level, source, datetime.now()])
