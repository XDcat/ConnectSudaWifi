> 免责声明：该脚本于 2020 年制作，已经稳定运行了几年，但肯定有不到位的地方。
> 如有您觉得哪里不合适，欢迎 PR。
# 脚本

| 脚本            | 描述         |
|---------------|------------|
|connect_suda_net.py               | 登录网关。      |
| reboot_mail.py | 电脑重启后发送邮件。 |


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