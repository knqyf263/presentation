#!/usr/bin/python
#coding:utf-8

from trello import TrelloClient
from pprint import pprint
from collections import defaultdict
from elasticsearch import Elasticsearch
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from pytz import timezone
from os.path import join, dirname
from dotenv import load_dotenv
import os

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = AP= os.environ.get("API_KEY")
API_TOKEN = AP= os.environ.get("API_TOKEN")
BOARD_ID = AP= os.environ.get("BOARD_ID")

count = defaultdict(lambda: 0)
length = defaultdict(lambda: 0)

today = datetime.now()

es = Elasticsearch("localhost:9200")

client = TrelloClient(API_KEY, token=API_TOKEN)
board = client.get_board(BOARD_ID)
members = board.all_members()

for m in members:
    member = client.get_member(m.id)
    d = datetime(2017, 4, 1, 0, 0)
    while True:
        since = d
        before = since + relativedelta(months=1)
        actions = client.fetch_json(
                    '/members/' + member.id + '/actions',
                    query_params={'limit': 1000, "since": since.strftime("%Y-%m-%d"), "before": before.strftime("%Y-%m-%d")})
        for a in actions:
            count[m.full_name] += 1
            utc_date = parse(a["date"])
            jst_date = utc_date.astimezone(timezone('Asia/Tokyo'))
            a["date"] = jst_date.strftime("%Y-%m-%dT%H:%M:%S%z")
            a["hour"] = jst_date.hour
            a["weekday"] = jst_date.weekday()
            if "text" in a["data"]:
                length[m.full_name] += len(a["data"]["text"])
                a["text_length"] = len(a["data"]["text"]) 
           # es.index(index="trello", doc_type=m.full_name, body=a)
        if today < before:
            break
        d = before

print "======= count ========="
for k, v in sorted(count.items(), key=lambda x: x[1], reverse=True):
    print k, v

print "======= length ========="
for k, v in sorted(length.items(), key=lambda x: x[1], reverse=True):
    print k, v

