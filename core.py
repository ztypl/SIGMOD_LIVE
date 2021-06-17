# coding: utf-8
# author: ztypl
# date:   2021/6/14

import json
import os
import subprocess
from urllib import request as urlrequest
import youtube_dl
import ffmpeg
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# GOOGLE_API_KEY = "AIzaSyAFfrMy-kteq_HNC4XOPtBzShYW6BfV5fs"
# CHANNEL_ID = "UC6HnOFC9ihT2uwwvetOJomw"
#
# proxy_host = "http://127.0.0.1:7890"
COOKIES_FILE = "data/cookies.json"


def read_info(filepath="data/info.json"):
    file = open(filepath, 'r')
    info = json.load(file, encoding='utf-8')
    file.close()
    return info


def set_proxy(proxy_host):
    os.environ['http_proxy'] = proxy_host
    os.environ['HTTP_PROXY'] = proxy_host
    os.environ['https_proxy'] = proxy_host
    os.environ['HTTPS_PROXY'] = proxy_host


def get_youtube_live_webpage(channel_id, google_api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?" \
          f"part=id&channelId={channel_id}&eventType=live&type=video&key={google_api_key}"
    try:
        req = urlrequest.Request(url)
        # req.set_proxy(proxy_host, 'http')
        # req.set_proxy(proxy_host, 'https')
        response = urlrequest.urlopen(req)
        res = json.loads(response.read().decode('utf8'))
        video_id = res['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    except:
        return ""


def get_youtube_live_info(original_url):
    if not original_url:
        return ""
    ydl = youtube_dl.YoutubeDL()
    result = ydl.extract_info(
        original_url,
        download=False,
    )
    if not result.get('is_live', False) or 'url' not in result:
        return ""
    # result['manifest_url']
    return result['url']


def get_bilibili_live_info(browser):
    room_setting_url = "https://link.bilibili.com/p/center/index#/my-room/start-live"
    browser.get(room_setting_url)
    live_status_button = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[@class="btn live-btn"]'))
    )
    if live_status_button.text == "开始直播":  # stopped
        print('房间当前未开播')
        checkbox = browser.find_element_by_xpath('//input[@id="checkbox"]')
        if not checkbox.is_selected():
            checkbox.click()
        category_toggle = browser.find_element_by_xpath('//a[@class="blink blue category-toggle"]')
        category_toggle.click()
        category_submit_button = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//button[@id="category-submit-btn"]'))
        )
        browser.find_element_by_link_text("学习").click()
        browser.find_element_by_link_text("科技科普").click()
        category_submit_button.click()
        title = browser.find_element_by_xpath('//input[@class="link-input title-input"]')
        title.clear()
        title.send_keys("SIGMOD/POD 2021")
        live_status_button.click()
        WebDriverWait(browser, 5).until(
            EC.text_to_be_present_in_element((By.XPATH, '//button[@class="btn live-btn"]'), "关闭直播")
        )
        print('已开始直播')

    rtmp_button = browser.find_element_by_xpath('//div[contains(@class, "rtmp")]/button')
    livecode_button = browser.find_element_by_xpath('//div[contains(@class, "live-code")]/button')

    return rtmp_button.get_attribute("data-clipboard-text") + livecode_button.get_attribute("data-clipboard-text")




def auto_login():
    print("正在自动登陆中...")
    old_cookies_file = open(COOKIES_FILE, "r", encoding='utf-8')
    json_cookie = json.loads(old_cookies_file.read())
    old_cookies_file.close()
    home_page_url = "https://bilibili.com"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    browser.get(home_page_url)
    for cookie in json_cookie:
        if "expiry" in cookie:
            cookie["expiry"] = int(cookie["expiry"])
        browser.add_cookie(cookie)
    browser.get(home_page_url)
    new_cookies = browser.get_cookies()
    json_cookies = json.dumps(new_cookies)
    new_cookies_file = open(COOKIES_FILE, "w", encoding='utf-8')
    new_cookies_file.write(json_cookies)
    new_cookies_file.close()
    try:
        if_sucess = browser.find_element_by_xpath(
            "/html/body/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/div[3]/div/div[1]/a/span")
        print("自动登陆成功！")
        return True, browser
    except NoSuchElementException:
        print("自动登录失败！")
        return False, browser


def manually_login():
    login_url = "https://passport.bilibili.com/login"
    input("按回车键开始手动登录...")
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    browser.get(login_url)
    input("若已完成手动登录，请按回车键继续...")
    cookies = browser.get_cookies()
    json_cookies = json.dumps(cookies)
    cookie_file = open(COOKIES_FILE, "w", encoding='utf-8')
    cookie_file.write(json_cookies)
    cookie_file.close()
    browser.close()
    # check_bilibili_cookie()


def have_cookie_file():
    try:
        open(COOKIES_FILE, "r", encoding='utf-8')
        return True
    except FileNotFoundError:
        return False


def push_livestream(youtube_link, push_link):
    popen = ffmpeg.input(youtube_link).output(
        push_link, vcodec='copy', acodec="aac", f='flv').run_async(
        pipe_stderr=True)
    for stdout_line in iter(popen.stderr.readline, b""):
        yield stdout_line
    popen.stderr.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, "ffmpeg process error")