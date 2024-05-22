#!/usr/bin/env bash
#依赖安装，运行一次就好
#0 8 5 5 * jd_indeps.sh
#new Env('依赖安装')
#

echo -e "安装脚本所需依赖，不一定一次全部安装成功，请自己检查\n"
echo -e "开始安装............\n"

npm install -g
npm install -g ds
npm install -g png-js
npm install -g date-fns
npm install -g axios@1.6.7
npm install -g crypto-js
npm install -g ts-md5
npm install -g tslib
npm install -g global-agent
npm install -g @types/node
npm install -g request
npm install -g jsdom
npm install -g moment
npm install -g cheerio
npm install -g dotenv
npm install -g got@11.8.6
npm install -g tough-cookie
npm install -g https-proxy-agent@7.0.2
npm install -g console-table-printer@2.12.0
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ jieba --no-cache-dir --break-system-packages
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ requests --no-cache-dir --break-system-packages
rm -rf /usr/local/npm-global/5/node_modules/.npm/canvas*
rm -rf /root/.local/share/npm/global/5/.npm/canvas*
echo -e "\n所需依赖安装完成，请检查有没有报错，可尝试再次运行"