from urllib import parse

def url_enco(text):
        enco = parse.quote(text) #문자열 인코딩
        
        return enco