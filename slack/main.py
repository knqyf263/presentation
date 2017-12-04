#!/usr/bin/python
#coding:utf-8

import glob
import json
import datetime
import os
from pprint import pprint
from collections import defaultdict
from elasticsearch import Elasticsearch
from pytz import timezone
from elasticsearch import helpers

es = Elasticsearch("localhost:9200")

EXPORT_DIR = "slack_export"

members = dict()
with open(os.path.join(EXPORT_DIR, "users.json")) as f:
    member_list = json.load(f)
    for member in member_list:
        if "real_name" in member:
            members[member["id"]] = member["real_name"]
        else:
            members[member["id"]] = member["name"]

actions = []
file_list = glob.glob(os.path.join(EXPORT_DIR, "*", "**"))
for file_name in file_list:
    with open(file_name) as f:
        message_list = json.load(f)
    for message in message_list:
        ts = float(message["ts"])
        d = datetime.datetime.fromtimestamp(ts)
        if "user" in message:
            user = message["user"]
            text = message["text"]
            message["username"] = members[user]
            message["text_length"] = len(text)
        jp = timezone('Asia/Tokyo')
        jst_date = jp.localize(d)
        message["date"] = jst_date
        message["hour"] = jst_date.hour
        message["weekday"] = jst_date.weekday()
        actions.append({'_index':'slack', '_type':'slack', '_source': message})
        if len(actions) > 1000:
            helpers.bulk(es, actions)
            actions = []

if len(actions) > 0:
    helpers.bulk(es, actions)
