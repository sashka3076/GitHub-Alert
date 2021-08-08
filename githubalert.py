#!/usr/bin/python3

# 群机器人的webhook写这里
webhooks = [
    "",

]

# 关键词写这里
keywords = [
    "CVE-2021-",
    "CVE-2020-",

]

import requests
import time
import os
import logging

# https://developers.dingtalk.com/document/robots/custom-robot-access
# https://work.weixin.qq.com/api/doc/90000/90136/91770


headers = {
    "Referer": "https://github.com/p7e4/GitHub-Alert",
    "User-Agent": "GitHub-Alert"
}


def die(msg):
    print(f"[{time.strftime('%Y-%m-%d %X')}] {msg}")
    exit()


def get_update(uptime, keyword):
    if not keyword: return
    uptime = time.strftime("%Y-%m-%dT%X", time.gmtime(uptime))
    api = f"https://api.github.com/search/repositories?q=created:%3E{uptime}%2b00:00 {keyword}&sort=updated"
    data = []
    for i in range(10):
        try:
            r = requests.get(api, timeout=100, headers=headers)
            if r.status_code == 200:
                for item in r.json()["items"]:
                    data.append([item["full_name"], item["html_url"], item["description"]])

                return data
            else:
                continue

        except Exception as e:
            print(e)
            time.sleep(10)

    die(f"api多次请求失败")


def main():
    runtime = time.time()
    if os.path.exists(".githubalert"):
        with open(".githubalert") as f:
            if data:=f.read():
                uptime = float(data)
            else:
                uptime = time.time() - 60 * 60 * 10
    else:
        uptime = time.time() - 60 * 60 * 10

    r = requests.get("https://api.github.com/rate_limit", timeout=30, headers=headers)
    limit = r.json()["resources"]["search"]
    remaining = limit["remaining"]
    reset = limit["reset"]

    for i in keywords:
        if remaining:
            remaining -= 1
        else:
            time.sleep(reset - time.time() + 1)
            reset += 60

        result = get_update(uptime, i)


        if result:
            send_notification(result)
            print(f"[{time.strftime('%Y-%m-%d %X')}] 关键词'{i}'，新增{len(result)}个项目")
        else:
            print(f"[{time.strftime('%Y-%m-%d %X')}] 关键词'{i}'，无更新项目")

    try:
        with open(".githubalert", "w") as f:
            f.write(str(runtime))
    except Exception as e:
        print(e)


def send_notification(msg):
    for i in msg[::-1]:
        for webhook in webhooks:
            if not webhook: continue
            if webhook.find("oapi.dingtalk.com") != -1:
                markdown = {
                    "title":"有新的GitHub监控消息",
                    "text": f"GitHub新项目: **[{i[0]}]({i[1]})**\n> {i[2]}"
                }
            elif webhook.find("qyapi.weixin.qq.com") != -1:
                markdown = {
                    "content": f"[{i[0]}]({i[1]})\n><font color=\"comment\">{i[2]}</font>\n\n"
                }
            else:
                die("未知的通知类型")

            tmp = {
               "msgtype": "markdown",
               "markdown": markdown
            }

            try:
                r = requests.post(webhook, json=tmp, timeout=20)
                if r.json()["errcode"] != 0:
                    print(f"发送消息失败: {r.text}")

            except Exception as e:
                die(f"发送消息请求失败\n{e}")

        if len(msg) > 20:
            time.sleep(3)


if __name__ == '__main__':
    main()

