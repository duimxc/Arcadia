# Arcadia辅助工具库

全量自用工具本，使用方法详解库说明，随缘更新~


> 官方线报频道：[Arcadia工具库](https://t.me/duimxc)

## 拉库

- ### Arcadia 面板

    ```bash
    arcadia repo Arcadia辅助工具库 https://github.com/duimxc/Arcadia.git main --updateTaskList true --whiteList '^arcadia_'
    ```
    详见官方文档：https://arcadia.cool

- ### 青龙面板

    ```bash
    ql repo https://github.com/duimxc/Arcadia.git "jd_" "" "^jd[^_]|sendNotify" "main"
    ```

## 功能配置

- ### Arcadia 面板

  ```bash
  export arcadia_api="http://IP:5678/openApi/cookie/delete" # IP:5678按照自己的Arcadia参数修改
  export arcadia_token="88888888" # 详见官方文档：https://arcadia.cool
  export white_list="pin1&pin2&...." # 白名单，在白名单中的CK不删除，及时更新CK
   ```

- ### 青龙面板

  ```bash
  export ARCADIA_API="http://IP:5678/openApi/updateCookie" # IP:5678按照自己的Arcadia参数修改
  export ARCADIA_TOKEN="88888888" # 详见官方文档：https://arcadia.cool
  ```

- ### Arcadia_Token 获取

  ```bash
  arcadia service info | grep ApiToken
  ```


__未经授权请勿搬运，脚本仅供用于学习交流，切勿用于商业用途！__
