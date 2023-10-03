#!/bin/bash
sudo docker run --name nlp-scylla -p 9042:9042 --hostname nlp-scylla -d scylladb/scylla --smp 1

read -p "User login:" login
read -p "Password:" pasw

sudo docker exec -t nlp-scylla cqlsh -u $login -p $pasw -f define.cql

echo "Server initialized successfully"
