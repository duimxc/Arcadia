#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: arcadia_CheckCK.py
Author: Duimxc
Date: 2023/11/10 10:00
TG: https://t.me/duimxc
cron: 0 30 * * * *
new Env('Arcadia面板失效CK检测删除');
"""

import os
import subprocess
import re
import requests
import urllib.parse
from sendNotify import *

# 定义要执行的bash命令
bash_command = "task cookie check"

# 定义API请求地址
openapi = os.environ.get("arcadia_api")

# 定义APIToken
openApiToken = os.environ.get("arcadia_token")

# 定义白名单
white_list = os.environ["white_list"].split('&')

# 定义消息
global msgs
msgs = ''

def inform():
    global msgs
    msgs += ("\n\n\n🔊🔊本程序由Duimxc提供🔊🔊")
    title = "Arcadia面板失效CK检测删除"
    send(title, msgs) 

# 使用Popen执行bash命令
process = subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# 查找包含关键词 "[×]" 的行，并提取pin信息
remove_pin = []
while True:
    output_line = process.stdout.readline()
    if not output_line and process.poll() is not None:
        break  # 命令执行完毕，退出循环
    if output_line:
        print(output_line.strip())  # 实时输出bash执行的信息

        # 在输出中检索关键信息，提取带有 "[×]" 关键词的pin信息
        if "[×]" in output_line:
            matches = re.findall(r'\d+\.\s*(.*?)\s+', output_line)
            if matches:
                # Remove ANSI escape codes from pin values
                clean_pins = [re.sub(r'\x1b\[\d+m', '', pin) for pin in matches]
                remove_pin.extend(clean_pins)

# 打印提取的pin信息（可选）
print("\n如下CK已经失效,将环境变量删除失效CK：")
for pin in remove_pin:
    print(pin)
    msgs += (f'【账号】{pin}已经失效，将从环境变量删除\n')

# 如果有失效的CK，才进行API请求
if remove_pin:
    for pin in remove_pin:
        for pin in white_list:
            print(f"账号{pin}在白名单中没有删除，请及时更新")
            msgs += (f"\n⛔账号{pin}在白名单中没有删除，请及时更新")
            continue
        url = openapi
        pin_str = urllib.parse.quote(pin, safe='/', encoding='utf-8')
        data = {
            "ptPins": [f"{pin_str}"]
        }
        headers = {
            'api-token': openApiToken
        }
        response = requests.post(url, headers=headers, json=data)

        # 解析响应数据
        try:
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 1:
                    cookie_count = result["data"]["cookieCount"]
                    account_count = result["data"]["accountCount"]
                    delete_count = result["data"]["deleteCount"]
                    print(f"成功删除账号{pin}。当前剩余 {account_count} 个账号和 {cookie_count} 个cookie。")
                    msgs += (f"\n✔删除账号{pin}成功。")
                else:
                    print(f"删除失败")
                    msgs += f"\n❌删除账号{pin}失败。"
            else:
                print(f"请求失败。状态码: {response.status_code}")
                msgs += f"\n🆘请求失败。状态码: {response.status_code}"
        except requests.exceptions.JSONDecodeError as e:
            print(f"解析API响应数据时出现错误: {e}")
            msgs += f"\n🆘解析API响应数据时出现错误: {e}"
        except Exception as e:
            print(f"发生未知错误: {e}")
            msgs += f"\n🆘发生未知错误: {e}"
    inform()
else:
    print("🟢没有失效的CK。")