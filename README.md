> 如有您觉得哪里不合适，欢迎 PR。
> 如果对你有用，不妨加个⭐

# 连接苏大网络
## 代码
* curl 版本
    ```bash
    curl "http://10.9.1.3:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C0%2C替换为学号&user_password=替换为密码9&wlan_user_ip=$(curl -s "http://10.9.1.3/" | grep -oE "v[46]+ip='(\d{1,3}\.){3}\d{1,3}'" | awk -F"'" '{print $2}')"
    ```
* wget 版本
    ```bash
    wget -q -O - "http://10.9.1.3:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C0%2C替换为学号&user_password=替换为密码&wlan_user_ip=$(wget -q -O - "http://10.9.1.3/" | grep -oE "v[46]+ip='(\d{1,3}\.){3}\d{1,3}'" | awk -F"'" '{print $2}' | head -n 1)"
    ```
## 原理
本质上就是一个 get 请求，需要三个参数：
* user_account 学号
* user_password 密码
* wlan_user_ip 设备的ip

但是 ip 需要实时获取，获取的方式就是请求 `http://10.9.1.3/`并解析。

## 推荐使用方法
在 linux 或者路由器中设置 crontab 定时任务，例如：
```bash
* * * * * wget -q -O - "http://10.9.1.3:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C0%2C替换为学号&user_password=替换为密码&wlan_user_ip=$(wget -q -O - "http://10.9.1.3/" | grep -oE "v[46]+ip='(\d{1,3}\.){3}\d{1,3}'" | awk -F"'" '{print $2}' | head -n 1)"
```
![路由器](https://github.com/XDcat/ConnectSudaWifi/blob/master/source/%E8%B7%AF%E7%94%B1%E5%99%A8%20crontab.png)
> 具体如何使用 crontab 请自行搜索。

# 远程桌面软件
推荐 Todesk，尽量不要使用 Microsoft Remote Desktop ！

原因：
Microsoft Remote Desktop 在连接时会改变系统分辨率，而不是串流软件，如果固定一台设备连接问题不大，当有多台设备远程访问时，会多次改变分辨率，
而导致死机，这时只能通过重启的方式解决。
