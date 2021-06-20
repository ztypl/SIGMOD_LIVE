import json
import time
from datetime import datetime

import requests

from core import *

mids = [
    '3979240',
    '319886910',
    '4429765',
    '302269243',
    '1286456',
    # '264409968'  # This is wenbo's uid, for test
]


COOKIES_DIR = "data/cookies"

headers = {'cookie': 'a'}

info = read_info("data/info.json")

while True:
    for i, mid in enumerate(mids):
        resp = requests.get(f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={mid}', headers=headers)
        live_status = resp.json()['data']['liveStatus']
        print(datetime.now())
        if live_status == 0:
            resp = requests.post('http://sms-api.luosimao.com/v1/send.json', auth=('api', 'key-79afd948d295f2be0a0869fd6507da4d'),
                                 data={'mobile': '18910149953', 'message': f'同学你好，你报名参加的 {i + 1} 活动将于一小时后开始，请前往 b站直播间中断 参加活动【水木汇】'})
            print(resp.text)
            resp = requests.post('http://sms-api.luosimao.com/v1/send.json', auth=('api', 'key-79afd948d295f2be0a0869fd6507da4d'),
                                 data={'mobile': '13051575731', 'message': f'同学你好，你报名参加的 {i + 1} 活动将于一小时后开始，请前往 b站直播间中断 参加活动【水木汇】'})
            print(resp.text)
        time.sleep(10)
