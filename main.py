from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import configparser
from scrappers.auth import auth_scylla

with auth_scylla() as session:
    rows = set([i.url for i in session.execute('SELECT url FROM URLS').all()])
    print(rows)
    print(len(rows))
