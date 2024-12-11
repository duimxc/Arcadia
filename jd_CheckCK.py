#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: jd_CheckCK.py
Author: Duimxc
Date: 2024/8/21 20:00
TG: https://t.me/duimxc
cron: 0 30 * * * *
new Env('青龙京东CK检测&&缓存Token');
"""
import json
import os
import random
import re
import time
from urllib.parse import unquote

import parse
import redis
import requests

token = ""
Token_url = "https://lzkj-isv.isvjcloud.com"
proxyUrl = "http://192.168.1.103:8080"

# 缓存Token文件路径
MCacheToken = "walle1798_EVE/tokens/"
KRCacheToken = "KingRan_KR/function/cache/token.json"
CiShanJiaToken = "SuperManito_cishanjia/function/token.json"
dy6yunToken = "6dylan6_jdpro/function/token.json"
RebelsToken = "9Rebels_jdmax/utils/token.json"
redlouToken = "DDredlou_redlou/utils/cache/token.json"
dy6manToken = "6dylan6_jdm/function/cache/token.json"
# redis
redis_url = "redis://default:xoefasdf11@192.168.1.103:6379/0"
# SIGN地址
SIGN_API = ""


def get_cookies():
    global token
    if os.path.exists("/ql/config/auth.json"):
        config = "/ql/config/auth.json"
    else:
        config = "/ql/data/config/auth.json"
    with open(config, encoding="utf-8") as f1:
        token = json.load(f1)['token']
    url = 'http://127.0.0.1:5600/api/envs'
    headers = {'Authorization': f'Bearer {token}'}
    body = {
        'searchValue': 'JD_COOKIE'
    }
    datas = requests.get(url, params=body, headers=headers).json()['data']
    return datas


def check(ck):
    checkurl = 'https://plogin.m.jd.com/cgi-bin/ml/islogin'
    headers = {
        "Accept": '*/*',
        "Accept-Encoding": 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        "Connection": 'keep-alive',
        "Cookie": ck,
        "Host": 'plogin.m.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/116.0.0.0',
    }
    # noinspection PyBroadException
    try:
        response = requests.post(url=checkurl, headers=headers)
        result = response.json()
        return result.get('islogin') == "1"
    except Exception:
        return False


def disable_ck(date):
    global token
    url = 'http://127.0.0.1:5600/api/envs/disable'
    headers = {'Authorization': f'Bearer {token}'}
    data = date
    code = requests.put(url, json=data, headers=headers)
    print(code)
    return


def requests_proxy(url, headers=None, data=None, proxy=None, method="post", max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            if method == "post":
                response = requests.post(url=url, headers=headers, data=data, verify=False, timeout=2, proxies=proxy)
            elif method == "get":
                response = requests.get(url=url, headers=headers, data=data, verify=False, timeout=2, proxies=proxy)

            if response.status_code == 200:
                return {
                    "status": response.status_code,
                    "data": response.text
                }
            else:
                print(f"⚠️请求失败，状态码: {response.status_code}")

        except Exception as e:
            # print("⚠️请求发生异常: ", e)
            pass
        proxy = getproxy(proxyUrl)
        retries += 1
        print(f"♻️尝试次数: {retries}/{max_retries}")
        # time.sleep(1)  # 可以添加延迟

    print("❌达到最大尝试次数，请求失败")
    return None


def get_sign(functionId, body):
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "fn": functionId,
        "functionId": functionId,
        "body": body
    })
    resp = requests.post(url=SIGN_API, headers=headers, data=data)
    if resp is None:
        return None
    if resp["status"] != 200:
        print("sign出现异常", resp["status"])
        return None
    resp_json = json.loads(resp["data"])
    if "body" in resp_json:
        return resp_json["body"]
    elif "data" in resp_json:
        return resp_json["data"]["body"]
    return None


def gettoken(ck):
    try:
        start_time = time.time()
        headers = {
            "X-Rp-Client": "android_3.0.0",
            "Connection": "keep-alive",
            "User-Agent": f"okhttp/3.{random.uniform(7, 16)}.{random.uniform(1, 16)};jdmall;android;"
                          f"version/12.0.{random.uniform(1, 16)};build/{random.uniform(1, 100000)};",
            "X-Referer-Package": "com.jingdong.app.mall",
            "Charset": "UTF-8",
            "X-Referer-Page": "com.jingdong.app.mall.WebActivity",
            "Accept-Encoding": "br,gzip,deflate",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "api.m.jd.com",
            "Cookie": ck
        }
        functionId = "isvObfuscator"
        data = {"id": "", "url": Token_url}
        sign = get_sign(functionId, data)
        if sign is None:
            print("获取sign出错")
            return None
        ip = getproxy(proxyUrl)
        url = f"https://api.m.jd.com/client.action?functionId={functionId}&{sign}"
        resp = requests_proxy(url, headers, f"body={parse.quote(json.dumps(data))}", proxy=ip)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"耗时：{elapsed_time:.2f}秒")
        resp_json = json.loads(resp["data"])
        if resp_json["code"] == "0" and resp_json["errcode"] == 0:
            return resp_json['token']
        print("⚠️isvObfuscator 接口发生异常: ", resp_json)
    except Exception as e:
        print("⚠️isvObfuscator 接口发生异常: ", e)
    return None


def getproxy(url):
    resp = requests.get(url)
    resp = resp.text.strip()
    first_line = resp.splitlines()[0].strip()
    proxies = f"http://{first_line}"
    return proxies


if __name__ == "__main__":
    redisConn = redis.from_url(redis_url)
    update_data = []
    jd_cookies = get_cookies()
    i = 0
    for jdck in jd_cookies:
        i += 1
        JD_Cookie = jdck['value']
        status = check(JD_Cookie)
        if not status:
            # noinspection RegExpAnonymousGroup
            match = unquote(re.search(r'pt_pin=([^;]+)', JD_Cookie).group(1))
            if match:
                pt_pin = match
                print(f"账号{i}:{pt_pin}已经失效，请及时更新")
                update_data.append(jdck['id'])
        else:
            # noinspection RegExpAnonymousGroup
            match = unquote(re.search(r'pt_pin=([^;]+)', JD_Cookie).group(1))
            if match:
                pt_pin = match
                print(f"账号{i}:{pt_pin}正常")
            redisConn.set(match, token, ex=1500)
    print(update_data)
    disable_ck(update_data)
    print(f"共计失效CK{len(update_data)}个,已经禁用")
    if redisConn is not None:
        redisConn.close()
        print("✅ Redis 已断开")
