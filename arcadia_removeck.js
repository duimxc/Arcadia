/*
自动删除无效账号
适用于旧版本Arcadia
*/

// 用户配置
const whiteListPin = ['']
const openApiToken = ''

const axios = require('axios').default
const querystring = require('querystring')
let cookiesArr = []
const needRemovePin = []

!(async () => {
    if (process.env.JD_COOKIE) {
        if (process.env.JD_COOKIE.indexOf('&') > -1) {
            cookiesArr = process.env.JD_COOKIE.split('&')
        } else if (process.env.JD_COOKIE.indexOf('\n') > -1) {
            cookiesArr = process.env.JD_COOKIE.split('\n')
        } else {
            cookiesArr = [process.env.JD_COOKIE]
        }
    }
    if (cookiesArr.length === 0) {
        console.log('没号就跑个锤子！')
        return
    }
    await concTask(3, cookiesArr, Main)
    if (needRemovePin.length > 0) {
        await cookie_delete(needRemovePin)
    }
})().catch((e) => console.log(e))

async function Main(cookie, index) {
    // 定义账号关联参数
    const pt_pin = getCookieValue(cookie, 'pt_pin')
    const UserName = decodeURIComponent(pt_pin)
    const title = `【账号${index}】${UserName}：` // 生成标题
    const loginStatus = await islogin(cookie)
    if (typeof loginStatus === 'boolean') {
        if (loginStatus) {
            console.log(`${title}有效 ✅`)
        } else {
            console.log(`${title}无效 ❌`)
            if (!whiteListPin.includes(pt_pin)) {
                needRemovePin.push(pt_pin)
            }
            return
        }
    } else {
        console.log(`${title}未知 ❓`)
        return
    }
}

async function islogin(cookie) {
    const res = await request({
        url: 'https://plogin.m.jd.com/cgi-bin/ml/islogin',
        method: 'GET',
        headers: {
            Accept: '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            Cookie: cookie,
            Host: 'plogin.m.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/122.0.0.0',
        },
        timeout: 30000,
    })
    if (!res.success) {
        console.log(res.error)
        return
    }
    if (!res.data) {
        console.log('无响应数据')
        return
    }
    const islogin = res.data?.islogin
    if (islogin === '1') {
        return true
    } else if (islogin === '0') {
        return false
    }
    return undefined
}

async function cookie_delete(ptPins) {
    const res = await request({
        url: 'http://127.0.0.1:5678/openApi/cookie/delete',
        method: 'POST',
        headers: {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/122.0.0.0',
            'api-token': openApiToken,
        },
        data: { ptPins },
        timeout: 30000,
    })
    if (!res.success) {
        console.log(res.error)
        return
    }
    if (!res.data) {
        console.log('无响应数据')
        return
    }
    if (res.data.code === 1) {
        const { cookieCount, deleteCount } = res.data.data
        console.log(`已删除${deleteCount}个过期账号，现存${cookieCount}个账号`)
    } else if (res.data.msg) {
        console.log(res.data.msg)
    } else {
        console.log(res.data)
    }
    return
}

function getCookieValue(cookieStr, fieldName) {
    if (!cookieStr || !fieldName) return ''
    const reg = new RegExp(fieldName + '=([^;]*)')
    const result = reg.exec(cookieStr.trim().replace(/\s/g, ''))
    return (result && result[1]) || ''
}

// prettier-ignore
async function concTask(a="3",t,n){const e=t.slice();let o=!1,s=0,c=0;async function i(t,a){t=await n(t,a);t&&("boolean"==typeof t||"object"==typeof t&&t?.runEnd)&&(o=!0),s--,r()}async function r(){for(;s<a&&0<e.length&&!o;){var t=e.shift();s++,await i(t,++c)}o&&await new Promise(t=>{const a=setInterval(()=>{0===s&&(clearInterval(a),t())},100)})}var l=Math.min(e.length,a),f=[];for(let t=0;t<l;t++){var v=e.shift();s++,c++,f.push(i(v,c))}await Promise.all(f),r(),await new Promise(t=>{const a=setInterval(()=>{0!==s&&!o||(clearInterval(a),t())},100)})}

// prettier-ignore
async function request(e){const t={success:!1,status:null,data:null,headers:null,error:null,connected:!1};try{if(!e||!e.url)return t.error="缺少必要的请求参数",t;Object.assign(axios.defaults,{headers:{common:{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}},maxContentLength:1/0,maxBodyLength:1/0,maxRedirects:1/0,timeout:6e4,transformResponse:[e=>{try{return JSON.parse(e)}catch{}try{var s,t=/[\w$.]+\(\s*({[\s\S]*?})\s*\)\s*;?/;if(t.test(e))return s=e.match(t)[1],JSON.parse(s)}catch{}return e}]}),e.body&&(e.data=e.body,delete e.body);for(const s of["data","params"])e[s]||delete e[s];e.method=(e.method||"get").toLowerCase(),!e.data||"object"!=typeof e.data||e.headers&&e.headers["Content-Type"]&&!e.headers["Content-Type"].includes("application/x-www-form-urlencoded")||(e.data=querystring.stringify(e.data)),await axios(e).then(e=>{t.success=!0,t.status=e.status,t.data=e.data,t.headers=e.headers,t.connected=!0}).catch(e=>{var s=e.response?(t.connected=!0,e.response.data&&(t.data=e.response.data),e.response.headers&&(t.headers=e.response.headers),`请求失败 [Response code ${e.response?.status}]`):e.request?e.code:e.message||"未知错误状态";t.error=s,t.status=e.response?.status||null})}catch(e){t.error=e.message||e}return t}
