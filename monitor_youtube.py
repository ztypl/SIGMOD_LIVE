import json
import time
import traceback
from datetime import datetime

import requests

from core import *

channel_ids = [
    'UC6HnOFC9ihT2uwwvetOJomw',
    'UCdGqN_CW8ye4x1kWd8I4MEQ',
    'UCwjDrhyDzo8BmtQz9zDZz3Q',
    'UCzT7b3f0qbfnJuu8gRvLeFg',
    'UCON-1bNFF0vNqZS0zrnUjyQ',
]

info = read_info("data/info.json")

retry = [0]

while True:
    try:
        for i, channel_id in enumerate(channel_ids):
            url = f"https://www.googleapis.com/youtube/v3/search?" \
                f"part=id&channelId={channel_id}&eventType=live&type=video&key={info['google_api_key']}"
            resp = requests.get(url)
            live_status = resp.json()['pageInfo']['totalResults']
            print(datetime.now())
            if live_status == 0:
                send(i + 1, 'Youtube直播间中断', retry)
            time.sleep(10)
    except Exception as e:
        send(i + 1, 'YouTube监测脚本未知错误', retry)
        print(resp.text)
        print(traceback.format_exc())
