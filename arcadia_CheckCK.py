#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: arcadia_CheckCK.py
Author: Duimxc
Date: 2024/5/17 23:00
TG: https://t.me/duimxc
cron: 0 30 * * * *
new Env('Arcadia京东CK检测（新）');
"""

import os
import re
import json

import requests

Auth_File = "/arcadia/config/auth.json"
with open(Auth_File, 'r', encoding='utf-8') as f:
    f = f.read()
    auth = json.loads(f)
api_token = auth.get("openApiToken")
base_url = "http://127.0.0.1:5678"


def get_cookies(compositeId):
    headers = {'api-token': api_token}
    url = f"{base_url}/api/open/env/v1/page?category=composite_value&search=pt_pin&size=99999&compositeId={compositeId}"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    result = response.json()
    data = result['result']['data']
    return data


def query():
    headers = {'api-token': api_token}
    url = f"{base_url}/api/open/env/v1/query?name=JD_COOKIE"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    result = response.json()
    if result['code'] == 1 and result['result']:
        return result['result'][0]['data']['id']
    else:
        raise ValueError("Query failed or no JD_COOKIE found")


def check(ck):
    checkurl = 'https://plogin.m.jd.com/cgi-bin/ml/islogin'
    headers = {
        "Accept": '*/*',
        "Accept-Encoding": 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        "Connection": 'keep-alive',
        "Cookie": ck,
        "Host": 'plogin.m.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/116.0.0.0',
    }
    try:
        response = requests.post(url=checkurl, headers=headers)
        result = response.json()
        return result.get('islogin') == "1"
    except Exception as e:
        return False


def changeStatus(data):
    url = f'{base_url}/api/open/env/v1/changeStatus'
    headers = {'api-token': api_token}
    data = {
        "id": data,
        "status": 0
    }
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()


if __name__ == "__main__":
    update_data = []
    try:
        id = query()
        print(id)
    except ValueError as e:
        print(e)
        exit()
    Cookie_data = get_cookies(id)
    Cookie_data.reverse()
    i = 0
    for item in Cookie_data:
        i += 1
        JD_Cookie = item['value']
        status = check(JD_Cookie)
        if not status:
            match = re.search(r'pt_pin=([^;]+)', JD_Cookie)
            if match:
                pt_pin = match.group(1)
                print(f"账号{i}:{pt_pin}已经失效，请及时更新")
                update_data.append(item['id'])
        else:
            match = re.search(r'pt_pin=([^;]+)', JD_Cookie)
            if match:
                pt_pin = match.group(1)
                print(f"账号{i}:{pt_pin}正常")
    changeStatus(update_data)
    print(f"共计失效CK{len(update_data)}个,已经禁用")
