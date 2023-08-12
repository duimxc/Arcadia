import logging
import os
import json
import asyncio

from telethon import TelegramClient, events
from cacheout import FIFOCache

# 日志基础配置
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)
logger = logging.getLogger("Dbot")
logger.setLevel(logging.INFO)

# 读取脚本目录
_script_dir = os.path.dirname(os.path.abspath(__file__))
_ConfigCar = os.path.join(_script_dir, "Dbot.json")

with open(_ConfigCar, encoding='utf-8') as f:
    Dbot_json = f.read()
    properties = json.loads(Dbot_json)

# 缓存
cache = FIFOCache(maxsize=properties.get("cache_size"))
# Telegram相关
api_id = properties.get("api_id")
api_hash = properties.get("api_hash")
log_id = properties.get("log_id")
user_id = properties.get("user_id")
# 监控相关
listen = properties.get("listen_in")
logger.info(f"监控的频道或群组-->{listen}")
scripts = properties.get("scripts")
queues = {}

# 初始化客户端
if properties.get("proxy"):
    if properties.get("proxy_type") == "MTProxy":
        proxy = {
            'addr': properties.get("proxy_addr"),
            'port': properties.get("proxy_port"),
            'proxy_secret': properties.get('proxy_secret', "")
        }
    else:
        proxy = {
            'proxy_type': properties.get("proxy_type"),
            'addr': properties.get("proxy_addr"),
            'port': properties.get("proxy_port"),
            'username': properties.get('proxy_username', ""),
            'password': properties.get('proxy_password', "")
        }
    client = TelegramClient("Dbot", api_id, api_hash, proxy=proxy, connection_retries=99999).start()
else:
    client = TelegramClient("Dbot", api_id, api_hash, connection_retries=99999).start()


@client.on(events.NewMessage(chats=[listen], pattern=r'(export\s?\w*=(".*"|\'.*\'))'))
async def handler(event):
    logger.info(event.raw_text)
    await client.send_message(log_id, '收到线报')
