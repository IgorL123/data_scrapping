from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import configparser


def auth_scylla(keyspace="main"):
   
   config = configparser.ConfigParser()
   config.read('config.ini')

   ip = config['scyllaDB']['ip']
   user = config['scyllaDB']['user']
   pasw = config['scyllaDB']['pasw']

   auth_provider = PlainTextAuthProvider(username=user, password=pasw)
   cluster = Cluster([ip], auth_provider=auth_provider)
   session = cluster.connect(keyspace)

   return session
