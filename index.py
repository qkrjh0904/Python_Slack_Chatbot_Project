#######################################################################################
#                                                                                     #
#                                                                                     #
#                             개인 프로젝트 import                                     #
#                                                                                     #
#######################################################################################

import secrete
import Python_Slack_Chatbot_Project.hi_funtion
#######################################################################################
#                                                                                     #
#                                                                                     #
#                             개인 프로젝트 import                                     #
#                                                                                     #
#######################################################################################


# -*- coding: utf-8 -*-
import re
import urllib.request
from urllib import parse
from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter

from slack.web.classes import extract_json
from slack.web.classes.blocks import *

import json
import csv
from operator import itemgetter

SLACK_TOKEN = secrete.oauth1
SLACK_SIGNING_SECRET = secrete.basic_secrete1


app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)


def crawl_image_in_url(text):
    #print(text[13:])
    text.strip()
    
    url = "https://haemukja.com/recipes?utf8=%E2%9C%93&sort=rlv&name=%EB%B3%B6%EC%9D%8C%EB%B0%A5" #+ #parse.quote(text) #임의 URL 현: 볶음밥.

    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")
    image_source = []
    image_blocks = [] 

    for src_source in soup.find_all("a", class_="call_recipe thmb"):
        image_source.append(src_source.find("img").get("src"))
    print(image_source)
    for block in range(len(image_source)):
        image_blocks.append(ImageBlock(image_url = image_source[block],alt_text="이미지가안뜰때보이는문구"))
    #print(image_blocks)  
    return (image_blocks)

# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]

    message = crawl_image_in_url(text)
    slack_web_client.chat_postMessage(
         channel=channel, 
         blocks=extract_json(message)
    )
   
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)