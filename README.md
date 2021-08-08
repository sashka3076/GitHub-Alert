# GitHub-Alert

GitHub项目监控脚本，使用钉钉/企业微信通知

## 使用

下载后修改打开`githubalert.py`
- 在`webhooks`部分填入群机器人的webhook
- 在`keywords`填入要监控的项目关键词

钉钉需要设置自定义关键词为`GitHub`

可使用`crontab`或`windows定时任务`来做定时执行

- 每小时: `0 * * * * python3 /root/githubalert.py >> githubalert.log`

