from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import configparser
from scrappers.auth import auth_scylla

with auth_scylla() as session:
    rows = session.execute('SELECT * FROM logstore')
    for row in rows:
        print(row)