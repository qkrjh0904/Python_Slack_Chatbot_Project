#######################################################################################
#                                                                                     #
#                                                                                     #
#                             개인 프로젝트 import                                     #
#                                                                                     #
#######################################################################################
import secrete
import url_encoding
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
def _crawl_food_chart(text, i):
    text.strip()
    hangle = re.compile('[^ㄱ-ㅣ가-힣]+')
    text = hangle.sub('',text)   
    keyword = url_encoding.url_enco(text) #한글을 URL인코딩 작업
    if(text is ""):
        return "잘못된 요리이름입니다! 한글로 요리이름을 입력해주세요!"

    url = secrete.URL + keyword

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    title = soup.find("ul", class_="lst_recipe").find_all("li")
    title_link = soup.find("ul", class_="lst_recipe").find_all("li")
    score = soup.find_all("span", class_="judge")
    time = soup.find_all("div", class_="time")
    btn_like = soup.find_all("button", class_="btn_like")

    keywords.append(str(i+1)+". " 
    + "<http://haemukja.com" + title_link[i].find("p").find("a")["href"] + "|"
    + title[i].find("p").find("strong").get_text().strip() + ">"
    + " / 해먹지수 : " + score[i].find("strong").get_text().strip()
    + " / ⌚: " + time[i].get_text().strip() 
    + " / 💗: " + btn_like[i].get_text().strip()
    )

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)

def crawl_image_in_url(text, i):
    image_source = []
    image_blocks = [] 

    text.strip()
    hangle = re.compile('[^ㄱ-ㅣ가-힣]+')
    text = hangle.sub('',text)
    if(text is ""):
        return "잘못된 요리이름입니다! 한글로 요리이름을 입력해주세요!"
    url = secrete.URL + keyword
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    for src_source in soup.find_all("a", class_="call_recipe thmb"):
        image_source.append(src_source.find("img").get("src"))
    print(image_source)
    image_blocks.append(ImageBlock(image_url = image_source[i],alt_text="이미지가안뜰때보이는문구"))

    return (image_blocks)

# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    for i in range (12):
        message = _crawl_music_chart(text, i)
        message2 = crawl_image_in_url(text, i)
        slack_web_client.chat_postMessage(
            channel=channel, 
            blocks=extract_json(message2)
        )
        slack_web_client.chat_postMessage(
            channel=channel,
            text=message
        )
        

# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)