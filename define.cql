CREATE KEYSPACE IF NOT EXISTS main 
WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor' : 1};

USE main;

CREATE TABLE IF NOT EXISTS CLPapers (
    id int,
    num_page int,
    url text,
    paper_text text,
    title text,
    author text,
    views int,
    downloads int,
    likes smallint, 
    dislikes smallint,
    year smallint,
    journal text,
    keywords set<text>,
    collected_ts timestamp,
    PRIMARY KEY(id, num_page)
) WITH comment='Entity for cyberleninka papers';

CREATE TABLE IF NOT EXISTS News (
    news_text text,
    url text,
    author text,
    title text,
    views int,
    keywords set<text>,
    category text,
    collected_ts timestamp,
    PRIMARY KEY (url, collected_ts)
) WITH comment='Entity for news';

CREATE TABLE IF NOT EXISTS TgPosts (
    created_date timestamp,
    message_raw text,
    message_lemm text,
    fwd_from text,
    views float,
    forwards float,
    source_ch text,
    collected_ts timestamp,
    message_id int,
    PRIMARY KEY (source_ch, created_date)
) WITH comment='Entity for telegram channel posts';

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
    VALUES ('Server initialized', 'INFO', 'root', toTimestamp(now()));
