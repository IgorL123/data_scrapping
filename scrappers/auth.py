from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import telethon
from telethon.sync import TelegramClient
import configparser


def auth_scylla(keyspace="main"):
    config = configparser.ConfigParser()
    config.read("config.ini")

    ip = config["Cluster"]["ip"]
    user = config["Cluster"]["user"]
    pasw = config["Cluster"]["pasw"]

    auth_provider = PlainTextAuthProvider(username=user, password=pasw)
    cluster = Cluster([ip], auth_provider=auth_provider)
    session = cluster.connect(keyspace)

    return session


def auth_tg_client():
    config = configparser.ConfigParser()
    config.read("config.ini")

    api_id = int(config["Telegram"]["api_id"])
    api_hash = config["Telegram"]["api_hash"]
    session_name = config["Telegram"]["session_name"]

    return TelegramClient(session_name, api_id, api_hash)
