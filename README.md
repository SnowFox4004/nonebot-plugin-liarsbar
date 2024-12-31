<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="./assets/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="91" height="16" viewBox="0 0 91 16" fill="none"><g opacity="1" transform="translate(0 0)  rotate(0 45.5 8)"><text><tspan x="0" y="13" font-size="12" line-height="0" fill="#EA5252" opacity="1" font-family="sans-serif" letter-spacing="0"  >N</tspan><tspan x="9.755859375" y="13" font-size="12" line-height="0" fill="#707070" opacity="1" font-family="sans-serif" letter-spacing="0"  >one</tspan><tspan x="31.587890625" y="13" font-size="12" line-height="0" fill="#EA5252" opacity="1" font-family="sans-serif" letter-spacing="0"  >B</tspan><tspan x="39.1171875" y="13" font-size="12" line-height="0" fill="#707070" opacity="1" font-family="sans-serif" letter-spacing="0"  >ot</tspan><tspan x="51.216796875" y="13" font-size="12" line-height="0" fill="#707070" opacity="1" font-family="sans-serif" letter-spacing="0"  > </tspan><tspan x="54.767578125" y="13" font-size="12" line-height="0" fill="#EA5252" opacity="1" font-family="sans-serif" letter-spacing="0"  >P</tspan><tspan x="62.109375" y="13" font-size="12" line-height="0" fill="#707070" opacity="1" font-family="sans-serif" letter-spacing="0" >lugin</tspan></text></g></svg></p>
</div>


<div align="center">

# nonebot-plugin-liarsbar

_✨ Liar's Bar 插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/SnowFox4004/nonebot-plugin-liarsbar.svg" alt="license">
</a> 
<a href="https://pypi.python.org/pypi/nonebot-plugin-liarsbar">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-liarsbar.svg" alt="pypi">
</a> 
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<img src="https://img.shields.io/github/issues/SnowFox4004/nonebot-plugin-liarsbar" alt="issues">

</div>

> 这是一个 nonebot2 插件，用于游玩`骗子酒馆liar's bar`


## 📖 介绍

和朋友进行一场勾心斗角的酒馆游戏

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-liarsbar

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-liarsbar
</details>

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-liarsbar
</details>

<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-liarsbar
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-liarsbar
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-liarsbar"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| LIARS_NUM_BULLET | False | 1 | 每个玩家枪内子弹数 | 

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 |参数| 说明 |
|:-----:|:----:|:----:|:----:|:----:|:----:|
| `/createroom` | 群员 | 否 | 群聊 | `[可选] 房间名` | 创建房间，自动成为房主 |
| `/startgame` | 房主 | 否 | 群聊 | `无` |与此房间中所有玩家开始一场游戏 |
| `/attend` | 群员 | 否 | 群聊 | `[必需] 房间名` |加入房间名为`房间名`参数的房间 |
| `/fp` | 游戏中当前操作玩家 | 否 | 群聊 | `[必需] 牌的序号` |打出`牌的序号`的牌，可以出多张牌，如`/fp 1 2 3`可打出三张牌 |
| `/zy` | 游戏中当前操作玩家 | 否 | 群聊 | `无` |质疑上家 |
| `/quitroom` | 群员 | 否 | 群聊 | `无`| 退出当前房间，若是房主自动转让，若是最后一名玩家则关闭房间 |

### 效果图
待施工
