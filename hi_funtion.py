import re

def hi_funtion(text):
    if text not in re.compile('[^ ㄱ-ㅣ가-힣]+')