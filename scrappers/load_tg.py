from auth import auth_scylla
from datetime import datetime
from time import sleep
import pandas as pd

PATH = "tg_chats.parquet"
dtf = pd.read_parquet(PATH, engine="pyarrow")
session = auth_scylla()

# rian_ru markettwits

with open("old_channels", "r") as file:
    channels = file.readlines()
    channels = [i.strip() for i in channels][14:]


dtf["fwd_from"] = dtf["fwd_from"].apply(lambda x: str(x) if x else None)

print("Starting")
for ch in channels:
    print(f"Start inserting {ch}")
    dtf["collected_ts"] = datetime.now()
    dtf["message_id"] = None
    data = dtf.where(dtf["source"] == ch).dropna(subset=["source"]).values
    stmt = session.prepare("""INSERT INTO tgposts (created_date, message_raw, message_lemm, fwd_from, 
        views, forwards, source_ch, collected_ts, message_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""")

    for i in data:
        session.execute(stmt, [x for x in i])
    print(f"Inserted {len(data)} rows for {ch} source")
    sleep(60)
