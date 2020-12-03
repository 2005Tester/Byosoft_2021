import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json


class DingTalkRobot:
    def __init__(self, base_url, url_report, signature):
        self.report = url_report
        self.sign = signature
        self.base_url = base_url

    # Add timestamp and signature in base url    
    def gen_url(self):
        timestamp = str(round(time.time() * 1000))
        secret = self.signature
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = "{0}&timestamp={1}&sign={2}".format(self.base_url, timestamp, sign)
        return url

    # Send link type message to dingtalk group, tittle and description: information to be shown in dingtalk pushed message, can be simple description of project
    def send_msg(self, tittle, description):
        msg_link = {
                    "msgtype": "link", 
                    "link": {
                                "text": description, 
                                "title": tittle, 
                                "picUrl": "", 
                                "messageUrl": self.url_report
                            }
                    }

        headers = {'Content-Type': 'application/json;charset=utf-8'}
        r = requests.post(url = self.gen_url(), data = json.dumps(msg_link), headers = headers)
        print(r)

