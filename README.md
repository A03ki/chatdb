# ChatDB for NLP

ChatDB is a toolkit to easily store the conversation such as chat messages in a database. You can use ChatDB as a way of storing text in a stage of collecting data for NLP.

DBMS: [Neo4j](https://neo4j.com)

## Installation

You can choose either A or B.

### A. The case to use Neo4j Desktop

If you will work on a host OS and use Neo4j Desktop, it is recommended to install ChatDB from the PyPI:

```bash
pip install chatdb
```

Download Neo4j Desktop from the following: [https://neo4j.com/download/](https://neo4j.com/download/)

### B. The case to use Neo4j on a Docker container

You can use Git to clone the repository from GitHub:

```bash
git clone https://github.com/A03ki/chatdb.git
cd chatdb
```


#### If you will work on a host OS:

```bash
pip install -e .
docker-compose up -d db
```

#### If you will work on a docker container:

```bash
docker-compose up -d
docker-compose exec app /bin/sh -c "[ -e /bin/bash ] && /bin/bash || /bin/sh"
```

## Usage

First, store the text data in a database.

```python
from chatdb import Graph, Status

# Create Status
s1 = Status(text="How are you today?")
s2 = Status(text="I’m okay, thanks. And you?")
s3 = Status(text="I’m awesome.")

# Construct a relationship between Statuses
s1.reply_from(s2)  # s2.reply_to(s1)
s2.reply_from(s3)  # s3.reply_to(s2)

# Create the handler for Neo4j
# Work on a docker container
graph = Graph("bolt://db:7687", password="your_password")

# Work on a host OS
# graph = Graph("bolt://localhost:7687", password="your_password")

# Store data
graph.merge(s2)
```

Next, extract the text from a database.

```python
from chatdb import Graph, TextOutputer, Status

graph = Graph("bolt://db:7687", password="your_password")
# graph = Graph("bolt://localhost:7687", password="your_password")

outputer = TextOutputer(graph)

print(outputer.match([Status]).extract_text())

print(outputer.match([Status]*2).extract_text())

print(outputer.match([Status]*3).extract_text())
```

Output:

```
[['I’m okay, thanks. And you?'], ['How are you today?'], ['I’m awesome.']]
[['I’m okay, thanks. And you?', 'I’m awesome.'], ['How are you today?', 'I’m okay, thanks. And you?']]
[['How are you today?', 'I’m okay, thanks. And you?', 'I’m awesome.']]
```

You can also use the Neo4j Browser to check data.

Try to go to `http://localhost:7474` in your web browser and run the query which is `MATCH (n:Status) RETURN n`.


![Check data at http://localhost:7474](https://raw.githubusercontent.com/A03ki/chatdb/main/docs/images/readme_usage_data_in_neo4j_browser.png)

How to delete all data: `MATCH (n:Status) DETACH DELETE n`

For more information on how to use Neo4j Browser, see [https://neo4j.com/developer/neo4j-browser/](https://neo4j.com/developer/neo4j-browser/).

## Support for collecting Tweet data

```bash
pip install tweepy
```

This example will store the timeline of Twitter, Inc and the tweet which this account are replying to.

```python
import tweepy
from chatdb import Graph, SimpleTweetStatus
from chatdb.tools import TweetArchiver

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)

graph = Graph("bolt://db:7687", password="your_password")
# graph = Graph("bolt://localhost:7687", password="your_password")

archiver = TweetArchiver(graph, SimpleTweetStatus)

statuses = api.user_timeline(screen_name="Twitter")
for status in statuses:
    in_reply_to_status_id_str = status.in_reply_to_status_id_str
    if in_reply_to_status_id_str:
        in_reply_to_status = api.get_status(in_reply_to_status_id_str)
        archiver.add_status(**in_reply_to_status._json)
    archiver.add_status(**status._json)
```

For more information on how to use Tweepy, see [Tweepy Documentation](http://docs.tweepy.org/en/latest/).
