```
curl "http://10.9.1.3:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C0%2C替换为学号&user_password=替换为密码9&wlan_user_ip=$(curl -s "http://10.9.1.3/" | grep -oE "v[46]+ip='(\d{1,3}\.){3}\d{1,3}'" | awk -F"'" '{print $2}')"
```



> 免责声明：该脚本于 2020 年制作，已经稳定运行了几年，但肯定有不到位的地方。
> 如有您觉得哪里不合适，欢迎 PR。

本项目原为个人使用，由于疫情缘故，身边的同学有远程访问学校资源的需要，因此将个人以往使用的方法分享出来。
由于时间原因，先把最核心的代码放了出来。其他可能的方法，也放在了后续更新列表中。

如果对你有用，不妨加个⭐

❗ 以下内容，后续更新...
* 远程控制的软件（frp、Microsoft Remote Desktop、todesk ...)
* Linux 一键安装脚本
* Windows 定时任务设置方法
* BIOS 设置断电自动启动（防止停电）
---
# 脚本

| 脚本            | 描述         |
|---------------|------------|
|connect_suda_net.py               | 登录网关。      |
| reboot_mail.py | 电脑重启后发送邮件。 |

需要修改脚本中的账号密码。


# 环境
* python3
* requests -> `pip install requests`
# 部署

## Linux
将脚本添加到 crontab 中定时运行，需要注意的是，需要提供 python 的完整路径，否则可能搜索不到对应 python。
* 添加定时任务方法 `crontab -e`
* 搜索 python 路径方法 `which python`

我的定时任务，`crontab -l`
```shell
# 每 10 分钟登录网关
*/10 * * * * /home/zlj/anaconda3/envs/Ponsol/bin/python /home/zlj/script/connect_suda_net.py --mail=auto
# 每天 6:00 登录网关
0 6 * * * /home/zlj/anaconda3/envs/Ponsol/bin/python /home/zlj/script/connect_suda_net.py
# 重启后登录网关
@reboot /home/zlj/anaconda3/envs/Ponsol/bin/python /home/zlj/script/connect_suda_net.py
# 重启后发送邮件通知
@reboot /home/zlj/anaconda3/envs/Ponsol/bin/python /home/zlj/script/reboot_mail.py
```

# 远程桌面软件
推荐 Todesk，尽量不要使用 Microsoft Remote Desktop ！

原因：
Microsoft Remote Desktop 在连接时会改变系统分辨率，而不是串流软件，如果固定一台设备连接问题不大，当有多台设备远程访问时，会多次改变分辨率，
而导致死机，这时只能通过重启的方式解决。
