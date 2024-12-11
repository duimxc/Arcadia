"""
cron: 0 0/20 * * * *
new Env('缓存Token');
"""

import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib import parse
from urllib.parse import unquote

import redis
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
必装依赖
requests
redis
不报错不安装
PySocks
"""
"""
实现规律UA  还是久佬提供建议 还没实现
支持库有 KR本地 慈善家redis和本地 环境redis 麦积本地 超人库redis
2023/11/26
添加 ProxyHttpOverHttps 开关针对go代理进行的修改，极大避免的脚本使用的403,如果使用的go版本并且是今天或者最新请开启，默认关闭
2023/11/16
协议使用http
2023/11/10 15:00
修复了一大堆问题
2023/11/10
作者太菜了，异步换成非异步
2023/11/9 19:50
添加代理监测，监测不通过切换 (超人队久佬 https://github.com/Jejz168/BoredPlay.git 库作者提供建议)
获取成功添加 1-4秒随机等待 (超人队久佬提供建议)
取消 Complete_Pause完成后等待时间
2023/11/9 19:00
修复不使用代理aiohttp-socks报错
2023/11/9 18:00
修复不能使用socks5 代理问题
需要安装依赖 aiohttp-socks
2023/11/9 2:40
修复几个报错
2023 /11/8 22:45
支持隧道代理 Tunnel_url
支持完成后等待时间 默认2秒  Complete_Pause
支持隧道代理403等待时间 默认30秒 Tunnel_Pause
支持是否启用代理默认启用 (感觉秒什么用给一些号特别少的人准备的开关) JD_PROXY_OPEN
隧道代理优先级低于api,设置隧道后不会调用api 
2023/11/7 21:30
修复kr 慈善家的过期时间key错误的值不同问题
pin正则表达式问题
2023/11/6 23:00
必安装依赖 aioredis aiohttp
可安装可不安装依赖 aiodns
依赖版本限制 Python 3.10 > cchardet
依赖版本限制 Python 3.10 <=  charset-normalizer
修复慈善家路径错误问题

2023/11/6 5:30
本地存储支持 M系列 KR 慈善家
远程redis普通模式支持 慈善家 环境
如果有其他库需要添加可以自己添加也可以 https://t.me/InteTU/184 留言 如果是本地存储提供本地存储路径和存储格式 如果是远程存储配合获取格式
慈善家
    不支持 JD_ISV_TOKEN_REDIS_CACHE_KEY 如果需要支持 https://t.me/InteTU/184 留言
    支持 获取JD_ISV_TOKEN_CUSTOM_CACHE 但是仅支持 .json文件
"""
# 获取 token的域名 默认是 https://lzkj-isv.isvjcloud.com ,"https://cjhy-isv.isvjcloud.com", "https://lzkj-isv.isvjd.com", "https://lzkj-isv.isvjcloud.com", "https://jinggeng-isv.isvjcloud.com", "https://txzj-isv.isvjcloud.com"];
Token_url = "https://lzkj-isv.isvjcloud.com"
ProxyHttpOverHttps = False  # 针对代理优化如果你使用的是go代理并且版本是2023/11/26或者更新版本请设置为 True
# 代理相关 不填写默认获取隧道代理
proxyUrl = None  # 代理API 使用http \n分割 只能提取一个
user_pass = None  # 账户:密码 如果不能自动白名单建议填写

Tunnel_url = "http://192.168.1.103:8080"  # 隧道代理, 如果填写隧道代理将会不获取代理api
Tunnel_Pause = 0  # 隧道代理如果403停止秒数
THREAD_COUNT = 10  # 线程数量
JD_PROXY_OPEN = 0  # 是否启动代理默认启动 非0都不启用 给家宽小白准备的

# M系列缓存Token路径 如果使用就 MCacheToken = "walle1798_EVE/tokens/"
MCacheToken = "walle1798_EVE/tokens/"

# KR系列缓存Token路径 如果使用就 KRCacheToken = "KingRan_KR/function/cache/token.json"
KRCacheToken = "KingRan_KR/function/cache/token.json"
# 慈善家 SuperManito/cishanjia库 默认读取 JD_ISV_TOKEN_REDIS_CACHE_URL
CiShanJiaToken = "SuperManito_cishanjia/function/token.json"
dy6yunToken = "6dylan6_jdpro/function/token.json"
RebelsToken = "9Rebels_jdmax/utils/token.json"
redlouToken = "DDredlou_redlou/utils/cache/token.json"
dy6manToken = "6dylan6_jdm/function/cache/token.json"
# 环境redis换成
redis_url = "redis://default:xoefasdf11@192.168.1.103:6379/0"  # redis://:Redis密码@127.0.0.1:6379" 默认读取 PRO_REDIS_URL 变量的

# 慈善家 SuperManito/cishanjia库 支持格式 优先慈善家变量后环境变量
if redis_url is None:
    redis_url = os.environ.get('JD_ISV_TOKEN_REDIS_CACHE_URL', None)
    if redis_url is None:
        redis_url = os.environ.get('PRO_REDIS_URL', None)

# 如果是 0 = JD_SIGN_API 1 =  JD_SIGN_KRAPI 2 = M_API_SIGN_URL
state = 0
# 获取Sign
JD_SIGN = os.environ.get("JD_SIGN_API", None)
if JD_SIGN is None:
    JD_SIGN = os.environ.get("JD_SIGN_KRAPI", None)
    state = 1
    if JD_SIGN is None:
        JD_SIGN = os.environ.get("M_API_SIGN_URL", None)
        state = 2
        if JD_SIGN is None:
            print("没有请填写 sign获取地址 JD_SIGN_API | JD_SIGN_KRAPI | M_API_SIGN_URL")
            sys.exit()
        else:
            print(f"📶当前使用的sign地址：{JD_SIGN}")
    else:
        print(f"📶当前使用的sign地址：{JD_SIGN}")
else:
    print(f"📶当前使用的sign地址：{JD_SIGN}")

Father_path = re.findall(f"(.*?/scripts/)", os.path.abspath(__file__))[0]

now = datetime.now()
print("⏰当前的日期和时间是：", now.strftime("%Y-%m-%d %H:%M:%S"))

# 自动识别
dirlist = os.listdir(Father_path)
if "walle1798_EVE" in dirlist:
    MCacheToken = Father_path + MCacheToken
    print("🔊识别到M系列Token 存放目录是: ", MCacheToken)
else:
    MCacheToken = None
if "KingRan_KR" in dirlist:
    KRCacheToken = Father_path + KRCacheToken
    print("🔊识别到KR Token 存放文件是: ", KRCacheToken)
else:
    KRCacheToken = None
if "6dylan6_jdpro" in dirlist:
    dy6yunToken = Father_path + dy6yunToken
    print("🔊识别到6dy 存放文件是: ", dy6yunToken)
else:
    dy6yunToken = None
if "SuperManito_cishanjia" in dirlist:
    CiShanJiaToken = Father_path + CiShanJiaToken
    print("🔊识别到慈善家 Token 存放文件是: ", CiShanJiaToken)
else:
    CiShanJiaToken = None
if "9Rebels_jdmax" in dirlist:
    RebelsToken = Father_path + RebelsToken
    print("🔊识别到9Rebels Token 存放文件是: ", RebelsToken)
else:
    RebelsToken = None
if "DDredlou_redlou" in dirlist:
    redlouToken = Father_path + redlouToken
    print("🔊识别到红楼 Token 存放文件是: ", redlouToken)
else:
    redlouToken = None
if "6dylan6_jdm" in dirlist:
    dy6manToken = Father_path + dy6manToken
    print("🔊识别到6dymax 存放文件是: ", dy6manToken)
else:
    dy6manToken = None
# 获取慈善家是否设置了 JD_ISV_TOKEN_CUSTOM_CACHE
if os.environ.get("JD_ISV_TOKEN_CUSTOM_CACHE", None) is not None:
    CiShanJiaToken = os.environ.get("JD_ISV_TOKEN_CUSTOM_CACHE", None)
    # 判断是否可RK一样
    if CiShanJiaToken == KRCacheToken:
        CiShanJiaToken = None
    if dy6yunToken == KRCacheToken:
        dy6yunToken = None
    if RebelsToken == KRCacheToken:
        RebelsToken = None
    if redlouToken == KRCacheToken:
        redlouToken = None
    if dy6manToken == KRCacheToken:
        dy6manToken = None


#

class Proxy:
    def __init__(self, url=None, user_pass=None, redis_url=None, Tunnel_url=None):
        self.proxies = None
        self.url = url
        self.user_pass = user_pass
        self.new_time: int = 0
        self.headers = {
            "Connection": "keep-alive",
            "User-Agent": f"okhttp/3.{random.uniform(7, 16)}.{random.uniform(1, 16)};jdmall;android;version/12.0.{random.uniform(1, 16)};build/{random.uniform(1, 100000)};",
            "Charset": "UTF-8",
            "Cache-Control": "no-cache",
        }
        self.redisConn = None
        self.redis_url = redis_url
        self.Tunnel_url = {"https": Tunnel_url}
        self.http_url_402 = "http://wifi.vivo.com.cn/generate_204"

    def getproxy(self):
        for i in range(0, 3):
            resp = fetch_url_with_proxy(url=self.url, headers=self.headers)
            if resp is None:
                continue
            if resp["status"] != 200:
                print(f"获取代理状态码: {resp['status']} 原因 {resp['data']} 延迟一秒等待")
                # 延迟一秒
                time.sleep(1)
            elif len(resp['data']) > 30:
                print("获取api长度超过限制", resp['data'])
                self.proxies = None
                return
            else:
                ip = str(resp['data']).rstrip('\n')
                if self.user_pass:
                    self.proxies = {"https": f"http://{self.user_pass}@{ip}"}
                else:
                    self.proxies = {"https": f"http://{ip}"}
                self.new_time = int(time.time()) + 40
                resp = self.http402()
                if resp != 204:
                    print(f"检测 {self.proxies} 不通过等待两秒切换新的")
                    time.sleep(2)
                    continue
                print(f"获取新代理: {self.proxies}")
                return

    def redis(self):
        if self.redis_url is None:
            print("❌没有配置获取到redis不尝试重新连接")
            return
        try:
            self.redisConn = redis.Redis.from_url(self.redis_url)
            print("✅redis已链接")
        except redis.exceptions.ConnectionError as e:
            print("redis链接地址不通")

    def use_proxy(self):
        """
        获取使用的代理
        :return:
        :rtype:
        """
        if JD_PROXY_OPEN != 0:
            return None
        if self.url is not None:
            if self.new_time < int(time.time()):
                print("代理超过40秒主动切换")
                self.getproxy()
                return self.proxies
            else:
                return self.proxies
        else:
            return self.Tunnel_url

    def http402(self):
        headers = {
            "Connection": "keep-alive",
            "User-Agent": f"okhttp/3.{random.uniform(7, 16)}.{random.uniform(1, 16)};jdmall;android;version/12.0.{random.uniform(1, 16)};build/{random.uniform(1, 100000)};",
            "Charset": "UTF-8",
            "Accept-Encoding": "br,gzip,deflate",
            "Cache-Control": "no-cache",
        }
        resp = fetch_url_with_proxy(url=self.http_url_402, headers=headers, proxy=self.proxies, method="get")
        if resp is None:
            return -1
        if resp["status"] == 204:
            return 204
        else:
            return -1


proxy = Proxy(url=proxyUrl, user_pass=user_pass, redis_url=redis_url, Tunnel_url=Tunnel_url)


def fetch_url_with_proxy(url, headers=None, data=None, proxy=None, method="post", max_retries=10):
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

        retries += 1
        print(f"♻️尝试次数: {retries}/{max_retries}")
        # time.sleep(1)  # 可以添加延迟

    print("❌达到最大尝试次数，请求失败")
    return None


def get_cookies():
    """
    获取CK
    :return:
    :rtype:
    """
    cookies = os.environ["JD_COOKIE"].split('&')
    random.shuffle(cookies)
    return cookies


def get_sign(functionId, body):
    global headers, data
    if state == 0 or state == 2:
        headers = {"Content-Type": "application/json"}
        data = json.dumps({
            "fn": functionId,
            "functionId": functionId,
            "body": body
        })
    elif state == 1:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        # 将 JSON 对象转换为 JSON 字符串
        data = {
            "fn": functionId,
            "functionId": functionId,
            "body": json.dumps(body),
        }
    resp = fetch_url_with_proxy(url=JD_SIGN, headers=headers, data=data)
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
    for i in range(0, 20):
        try:
            start_time = time.time()
            headers = {
                "X-Rp-Client": "android_3.0.0",
                "Connection": "keep-alive",
                "User-Agent": f"okhttp/3.{random.uniform(7, 16)}.{random.uniform(1, 16)};jdmall;android;version/12.0.{random.uniform(1, 16)};build/{random.uniform(1, 100000)};",
                "X-Referer-Package": "com.jingdong.app.mall",
                "Charset": "UTF-8",
                "X-Referer-Page": "com.jingdong.app.mall.WebActivity",
                "Accept-Encoding": "br,gzip,deflate",
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "api.m.jd.com",
                "Cookie": ck
            }
            if ProxyHttpOverHttps:
                headers['Proxy-Http-Over-Https'] = True
            functionId = "isvObfuscator"
            data = {"id": "", "url": Token_url}
            sign = get_sign(functionId, data)
            if sign is None:
                continue

            ip = proxy.use_proxy()
            url = f"https://api.m.jd.com/client.action?functionId={functionId}&{sign}"

            resp = fetch_url_with_proxy(url, headers, f"body={parse.quote(json.dumps(data))}",
                                        proxy=ip)
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"耗时：{elapsed_time:.2f}秒")
            if resp is None:
                print("正在重试{i+1}")
                continue
            #    print("isvObfuscator 接口响应:", resp)
            if resp["status"] != 200:

                if resp["status"] == 403:
                    if proxy.Tunnel_url["https"] is None:
                        print("代理超过403了切换代理")
                        proxy.getproxy()
                    else:
                        # 隧道代理停止秒
                        time.sleep(Tunnel_Pause)
                continue
            resp_json = json.loads(resp["data"])
            if resp_json.get("code") == "3" and resp_json.get("errcode") == 264:
                print("账号失效了")
                return "账号失效"
            if resp_json["code"] == "0" and resp_json["errcode"] == 0:
                return resp_json['token']
            print("⚠️isvObfuscator 接口发生异常: ", resp_json)


        except Exception as e:
            print("⚠️isvObfuscator 接口发生异常: ", e)
    return None


def m_token(pin, token):
    if MCacheToken is None:
        return
    var = {"expireTime": int(time.time() * 1000) + 1740000, "token": token}
    with open(f"{MCacheToken}{pin}.json", "w", encoding="utf-8") as f:
        json.dump(var, f)
    print(f"M系列缓存 {unquote(pin)} 的token 成功")


def kr_token(path_token, KR):
    if path_token is None:
        return
    try:
        with open(path_token, "w", encoding="utf-8") as f:
            json.dump(KR, f, indent=4, ensure_ascii=False)
        print(f"✅{path_token} 路径缓存 的token 成功")
    except Exception as e:
        print(f"❌{path_token} 路径缓存 的token 发生异常: ", e)


def fetch_token(ck):
    token = gettoken(ck)
    if token == "账号失效":
        print("❌账号失效跳过获取, ", ck)
        return None, ck
    if token is None:
        print("❌获取次数过多跳过获取, ", ck)
        return None, ck

    pt_pin_match = unquote(re.search(r'pin=(.*?);', ck).group(1))
    return token, pt_pin_match


def main_async():
    token_Path = [KRCacheToken, CiShanJiaToken, dy6yunToken, RebelsToken, redlouToken, dy6manToken]
    KR = {}

    # 检查代理设置
    if proxy.Tunnel_url["https"] is None and proxy.url is None and JD_PROXY_OPEN == 0:
        print("你设置的使用代理但是没有设置隧道代理或者 API")
        return

    # 使用代理
    proxy.use_proxy()

    # 连接 Redis
    proxy.redis()

    # 获取 cookies
    cks = get_cookies()
    if cks is None:
        return

    # 使用多线程获取 token
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        future_to_ck = {executor.submit(fetch_token, ck): ck for ck in cks}
        for future in as_completed(future_to_ck):
            token, pt_pin_match = future.result()
            if token is None:
                continue

            # 写入 token
            m_token(pt_pin_match, token)

            # 记录 KR
            KR[pt_pin_match] = {
                "expires": int(time.time() * 1000) + 1740000,
                "val": token
            }

            # 环境的开始实现
            if proxy.redisConn is not None:
                try:
                    proxy.redisConn.set(pt_pin_match, token)
                    proxy.redisConn.expire(pt_pin_match, 1500)
                    # print(f"redis {pt_pin_match}缓存成功")
                except Exception as e:
                    print("❌写入 Redis 失败: ", e)

    if KR != {}:
        for path_token in token_Path:
            kr_token(path_token, KR)
    if proxy.redisConn is not None:
        proxy.redisConn.close()
        print("✅ Redis 已断开")


if __name__ == '__main__':
    main_async()
