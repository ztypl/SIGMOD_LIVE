import json
import time
import traceback
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

headers = {'cookie': 'a'}

retry = [0]

while True:
    try:
        for i, mid in enumerate(mids):
            resp = requests.get(f'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={mid}', headers=headers)
            live_status = resp.json()['data']['liveStatus']
            print(datetime.now())
            if live_status == 0:
                send(i + 1, 'b站直播间中断', retry)
            time.sleep(10)
    except Exception as e:
        send(i + 1, 'b站监测脚本未知错误', retry)
        print(resp.text)
        print(traceback.format_exc())
