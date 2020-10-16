cd /root/VideoRSS/ 
python3 main.py 
cp -f feed.xml /var/www/html/feed.xml
time=$(date "+%Y%m%d-%H%M%S")
echo "${time}"

