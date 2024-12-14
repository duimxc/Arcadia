#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: jd_Arcadia.py
Author: Duimxc
Date: 2024/12/14 14:00
TG: https://t.me/duimxc
cron: 0 30 * * * *
new Env('青龙JD_COOKIE传输到Arcadia');
1 初始
1.1 修复自动创建环境变量组没有指定分隔符导致的错误，现在默认使用&分隔符，不再需要手动指定。自动创建只有在没有环境变量组时才会执行。
"""

import os
import re
import time
import urllib.parse

import requests

api_token = os.environ["ARCADIA_TOKEN"]
base_url = os.environ["ARCADIA_API"]


def get_cookies():
    CookieJDs = []
    if os.environ.get("JD_COOKIE"):
        print("已获取并使用Env环境 Cookie")
        if '&' in os.environ["JD_COOKIE"]:
            CookieJDs = os.environ["JD_COOKIE"].split('&')
        elif '\n' in os.environ["JD_COOKIE"]:
            CookieJDs = os.environ["JD_COOKIE"].split('\n')
        else:
            CookieJDs = [os.environ["JD_COOKIE"]]
    else:
        if os.path.exists("JD_COOKIE.txt"):
            with open("JD_COOKIE.txt", 'r') as f:
                JD_COOKIEs = f.read().strip()
                if JD_COOKIEs:
                    if '&' in JD_COOKIEs:
                        CookieJDs = JD_COOKIEs.split('&')
                    elif '\n' in JD_COOKIEs:
                        CookieJDs = JD_COOKIEs.split('\n')
                    else:
                        CookieJDs = [JD_COOKIEs]
                    CookieJDs = sorted(set(CookieJDs), key=CookieJDs.index)
        else:
            print("未获取到正确✅格式的京东账号Cookie")
            return None

    print(f"====================共{len(CookieJDs)}个京东账号Cookie=========\n")
    print(
        f"=================="
        f"脚本执行- 北京时间(UTC+8)：{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}"
        f"=====================\n")
    return CookieJDs


def create():
    headers = {'api-token': api_token}
    data = {
        "category": "composite",
        "data": {
            "type": "JD_COOKIE",
            "separator": "&"
        }
    }
    url = f"{base_url}/api/open/env/v1/create"
    response = requests.post(url=url, headers=headers, json=data)
    response.raise_for_status()


def query():
    headers = {'api-token': api_token}
    url = f"{base_url}/api/open/env/v1/query?name=JD_COOKIE"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    result = response.json()
    if result['code'] == 1 and result['result']:
        return result['result'][0]['data']['id']
    else:
        print("未查询到JD_COOKIE，开始创建。")
        create()


def queryMember(id, value):
    headers = {'api-token': api_token}
    encoded_value = urllib.parse.quote(value)
    url = f"{base_url}/api/open/env/v1/queryMember?id={id}&value={encoded_value}"
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()
    result = response.json()
    if result['code'] == 1 and result['result']:
        return result['result'][0]['id']
    return None


def update(data):
    headers = {'api-token': api_token}
    url = f"{base_url}/api/open/env/v1/update"
    payload = {
        "category": "composite_value",
        "data": data
    }
    response = requests.post(url=url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result['result']


def create_value(data, compositeId):
    headers = {'api-token': api_token}
    url = f"{base_url}/api/open/env/v1/create"
    payload = {
        "category": "composite_value",
        "data": data,
        "compositeId": compositeId
    }
    response = requests.post(url=url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    if isinstance(result['result'], dict):  # If a single item was created
        return 1
    else:  # If multiple items were created
        return result['result']['count']


if __name__ == "__main__":
    update_data = []
    create_data = []
    CookieJDs = get_cookies()
    if not CookieJDs:
        print("没有找到有效的 Cookie，脚本结束。")
        exit()

    try:
        id = query()
    except ValueError as e:
        print(e)
        exit()

    for CookieJD in CookieJDs:
        match = re.search(r'pt_pin=([^;]+)', CookieJD)
        if match:
            pt_pin = match.group(1)
        else:
            continue

        member_id = queryMember(id, pt_pin)
        if member_id:
            update_data.append({"id": member_id, "group_id": id, "value": CookieJD, "enable": 1})
        else:
            create_data.append({"value": CookieJD})

    print("Update Data:", update_data)
    print("Create Data:", create_data)

    if update_data:
        updated_items = update(update_data)
        print(f"更新了 {len(updated_items)} 个项目。")
    if create_data:
        created_count = create_value(create_data, id)
        print(f"新建了 {created_count} 个项目。")
