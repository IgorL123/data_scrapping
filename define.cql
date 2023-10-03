CREATE KEYSPACE IF NOT EXISTS main 
WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor' : 1};

USE main;

CREATE TABLE IF NOT EXISTS CLPapers (
    id int PRIMARY KEY,
    paper_text text,
    title text,
    author text,
    likes smallint, 
    dislikes smallint,
    year smallint,
    journal text,
    keywords set<text>,
    collected_ts timestamp

) WITH comment='Entity for cyberleninka papers';

CREATE TABLE IF NOT EXISTS News (
    id int PRIMARY KEY,
    new_text text,
    url text,
    source text, 
    collected_ts timestamp,
    info blob

) WITH comment='Entity for news';

CREATE TABLE IF NOT EXISTS Urls(
    url text PRIMARY KEY,
    scrapped boolean,
    collected_ts timestamp

) with comment='Collecting urls that should be parsed';

CREATE TABLE IF NOT EXISTS Definitions(
    word text PRIMARY KEY,
    meanings set<text>,
    examples set<text>,
    common_part text,
    num_classes smallint

) with comment='Stored definitions';

CREATE TABLE IF NOT EXISTS LogStore(
    created_ts timestamp, 
    msg text, 
    level text, 
    source text,
    PRIMARY KEY (created_ts, msg, level, source)
);

INSERT INTO LogStore (msg, level, source, created_ts) 
    VALUES ("Server initialized", "INFO", "root", toTimestamp(now()));
