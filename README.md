# 视频订阅器
从我的需求出发写的rss订阅器，目前支持bilibili，bimiacg和tx订阅单剧，系列剧集暂无法全部订阅。  
# 使用方法 
1. 将`main.py` 文件放到服务器某一文件夹(假定为VideoRSS)下，最好在给予744权限  
    ```
    apt install -y git
    cd ~
    git clone https://github.com/wjcwqc/VideoRSS
    chmod 774 VideoRSS
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
    run.sh
    
    ``` 
    cd ~/VideoRSS
    python3 main.py 
    cp -f feed.xml /var/www/html/feed.xml
    ```

1. finish already
