# 视频订阅器
从我的需求出发写的rss订阅器，目前支持
bilibili番剧剧集
bimiacg
腾讯视频剧集

# 使用方法 
1. 将`main.py` 文件放到服务器某一文件夹(假定为VideoRSS)下，最好在给予755权限  
    ```
    sudo apt install -y git
    cd ~
    git clone https://github.com/wjcwqc/VideoRSS
    chmod 755 VideoRSS
    cd VideoRSS
    ```
1. 创建feed.xml和list.json 两个文件，写入以下内容
    
    feed.xml:
    ```
    <?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
        <channel>
            <title>
        频道名称
            </title>
            <link>
                https://github.wjcwqc.com/
            </link>
            <description>Whatever
            </description>
            <copyright>Copyright(C) wjcwqc
            </copyright>
    
        </channel>
    
    </rss>
    ```
    list.json  
    ```
    {
      "subscribe": [
        "订阅url1"，
        "订阅url2"
      ],
      "lastest": {
      }
    }
    ```
    1. 安装并配置nginx
    ```
    apt install -y nginx 
    service nginx start 
    systemctl enable nginx 
    ```

1. 编辑启动脚本并添加到cron

    

1. finish already
