# coding: utf-8
# author: ztypl
# date:   2021/6/17

import time
import requests
from core import *


def send(code, msg):
    print(msg)
    resp = requests.post('http://sms-api.luosimao.com/v1/send.json', auth=('api', 'key-79afd948d295f2be0a0869fd6507da4d'),
                         data={'mobile': '18910149953', 'message': f'同学你好，你报名参加的 {code} 活动将于一小时后开始，请前往 {msg} 参加活动【水木汇】'})
    print(resp.text)
    resp = requests.post('http://sms-api.luosimao.com/v1/send.json', auth=('api', 'key-79afd948d295f2be0a0869fd6507da4d'),
                         data={'mobile': '13051575731', 'message': f'同学你好，你报名参加的 {code} 活动将于一小时后开始，请前往 {msg} 参加活动【水木汇】'})
    print(resp.text)
    exit(1)


info = read_info("data/info.json")

set_proxy(info['proxy_host'])

while True:
    try:
        if not have_cookie_file():
            print('无Cookies文件，首次需要手动登录')
            manually_login()
        status, browser = auto_login()

        if not status:
            print('自动登录失败，请手动删除data/cookies.json后重试或联系管理员')
            exit(1)

        print("1. 获取YouTube直播网页")
        youtube_webpage = get_youtube_live_webpage(info['channel_id'], info['google_api_key'])
        if not youtube_webpage:
            send(info['room_id'], "未查询到Youtube直播间")

        print("2. 打开bilibili直播间")
        push_link = get_bilibili_live_info(browser)

        print("3. 获取YouTube直播流")
        youtube_link = get_youtube_live_info(youtube_webpage)
        if not youtube_link:
            send(info['room_id'], "无法获取到直播流，请检查代理后重试")
    except Exception:
        send(info['room_id'], '未知错误')
    try:
        print("4. 开始推流")
        for line in push_livestream(youtube_link, push_link):
            line_str = line.decode('gbk')
            if line_str.startswith('[hls'):
                #     print(line_str.split('\r')[0], flush=True, end='\n')
                continue
            # print(line, flush=True)
            print(line_str, flush=True, end='')
    except subprocess.CalledProcessError:
        print("推流出现异常，正在重启脚本...")
        time.sleep(10)      # sleep for 10 secs
        continue

    # exit(0)
    # send(0, '脚本退出')
