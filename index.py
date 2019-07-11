#######################################################################################
#                                                                                     #
#                                                                                     #
#                             개인 프로젝트 import                                     #
#                                                                                     #
#######################################################################################
import secrete

#######################################################################################
#                                                                                     #
#                                                                                     #
#                             개인 프로젝트 import                                     #
#                                                                                     #
#######################################################################################


# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter

from slack.web.classes import extract_json
from slack.web.classes.blocks import *

import json
import csv
from operator import itemgetter

SLACK_TOKEN = secrete.SLACK_TOKEN
SLACK_SIGNING_SECRET = secrete.SLACK_SIGNING_SECRET


app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)


# 크롤링 함수 구현하기
def _crawl_music_chart(text):
    if not "food" in text:
        return "`@<봇이름> food` 과 같이 멘션해주세요."

    url = "http://haemukja.com/recipes?name=%EB%B3%B6%EC%9D%8C%EB%B0%A5&sort=rlv&utf8=%E2%9C%93"

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    score = soup.find_all("span", class_="judge")
    time = soup.find_all("div", class_="time")
    btn_like = soup.find_all("button", class_="btn_like")
    for i in range(12):
        keywords.append(str(i+1)+"위 - " 
        + " / 해먹지수 : " + score[i].find("strong").get_text().strip()
        + " / 조리시간 : " + time[i].get_text().strip() 
        + " / 좋아요 수 : " + btn_like[i].get_text().strip()
        )

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)




# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    
    message = _crawl_music_chart(text)
    slack_web_client.chat_postMessage(
        channel=channel,
        text=message
    )
    
    # slack_web_client.chat_postMessage(
    #     channel = event_data["event"]["channel"],
    #     text = "<http://www.naver.com|여기를 클릭하세요> => 네이버입니다"
    #     # text = "*진한 글씨* _비스듬한 글씨_ ~취소선~ `print(source code)`"
    # )
    
    # block1 = ImageBlock(image_url="https://previews.123rf.com/images/isselee/isselee1101/isselee110100100/8652164-%ED%9D%B0%EC%83%89-%EB%B0%B0%EA%B2%BD-%EC%95%9E%EC%9D%98-%ED%86%A0%EB%81%BC-%ED%86%A0%EB%81%BC.jpg",alt_text="이미지가안뜰때보이는문구")
    # block2 = SectionBlock(fields=["text1", "text2"])
    # my_blocks= [block1, block2]
    # slack_web_client.chat_postMessage(
    #     channel=channel, 
    #     blocks=extract_json(my_blocks)
    # )

    # 다른 사람이 메시지를 올렸을 때, 그 사람에게만 답장하기
    # 참고: https://api.slack.com/methods/chat.postEphemeral    
    # slack_web_client.chat_postEphemeral(
    #     channel=channel,
    #     user=event_data["event"]["user"],
    #     text="조용히 하세요!"
    # )

    ## name으로 id값 받아오기
    # text = ["slackbot", "hyena", "qkrjh0904"]
    # response = slack_web_client.users_list()
    # for user in response["members"]:
    #     if user["name"] in text:
    #         slack_web_client.chat_postMessage(
    #             channel = channel,
    #             text = user["name"] + " : " + user["id"]
    #         )
    #         slack_web_client.chat_postEphemeral(
    #             channel="channel", user=user_id, text="뭐하고 있니?"
    #         )

# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)