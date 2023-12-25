from time import sleep
import telethon
from auth import auth_tg_client
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
from base import BaseScrapper


class TgScrapper(BaseScrapper):
    """
    Collecting texts from telegram channels
    """

    def __init__(self):
        BaseScrapper.__init__(self)

    def get_channels(self):
        with open("new_channels", "r") as file:
            channels = file.readlines()
        return [i.strip() for i in channels]

    def collect(self):

        client = auth_tg_client()
        client.start()
        ''' Ограничение примерно в 500 каналов '''

        channels = self.get_channels()
        self.log(f"Ready to scrapp {len(channels)} telegram channels", level="INFO", source="tg_scrapper")
        for i in range(len(channels)):
            try:

                min_id = self.session.execute(f"""select min(message_id) as min_id from tgposts 
                                                  where source_ch = '{channels[i]}' ALLOW FILTERING""").one().min_id
                if min_id == 0:
                    continue


                channel_entity = client.get_input_entity(channels[i])
                post = client(GetHistoryRequest(
                        peer=channel_entity,
                        limit=100,
                        offset_date=None,
                        offset_id=min_id,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0))
                messages = post.messages
                count = 0
                stmt = self.session.prepare("""INSERT INTO tgposts (created_date, message_raw, message_lemm, fwd_from, 
                                           views, forwards, source_ch, collected_ts, message_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""")
                for message in messages:
                    msg = message.to_dict()
                    if "message" in msg:
                        if msg["message"] != "":
                            to_insert = [
                                msg["date"],
                                msg["message"],
                                None,
                                str(msg["fwd_from"]) if msg["fwd_from"] else None,
                                float(msg["views"]),
                                float(msg["forwards"]),
                                channels[i],
                                datetime.now(),
                                msg["id"]
                            ]
                            count += 1
                            self.session.execute(stmt, to_insert)

                self.log(f"Collected {count} messages from {channels[i]}", level="INFO", source="tg_scrapper")

            except (ValueError, KeyError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, TypeError,
                    telethon.errors.rpcerrorlist.ChannelPrivateError,
                    telethon.errors.rpcerrorlist.UsernameInvalidError) as error:
                self.log(f"Other error occurred: {error}", level="ERROR", source="tg_scrapper")

            except telethon.errors.rpcerrorlist.FloodWaitError as e:
                self.log(f"Flood detected: {e}", level="ERROR", source="tg_scrapper")
                break
        sleep(self.sleep_time * 2)


if __name__ == "__main__":
    run = TgScrapper()
    run.collect()

