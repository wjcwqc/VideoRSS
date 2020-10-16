import requests
from bs4 import BeautifulSoup as bsp
import json
import xml.etree.ElementTree as ET
import time

urlist = {'v.qq.com': 'tencent',
          'www.bilibili.com': 'bilibili',
          'www.bimiacg.com': 'bimiacg',
          'manga.bilibili.com': 'bilimanga',
          'space.bilibili.com': 'bilichannel'
          }
bilimd = "https://api.bilibili.com/pgc/review/user?media_id="
biliss = "https://api.bilibili.com/pgc/web/season/section?season_id="
bimilink = "http://www.bimiacg.com"


class TencentLenError(Exception):
    def __init__(self, message='text is not as long as contents'):
        super().__init__(message)
        self.message = message


class UpdateInfo:
    # 一步到位，数据采集
    def __init__(self, url):
        self.url = url
        getattr(self, self.recognize())()
        self.info = {
            'title': self.title,
            'plantform': self.plantform,
            'episode': self.ep,
            'link': self.link
        }

    def updatefeed(self, feedsrc):
        nowele = ET.SubElement(feedsrc[0], 'item')
        ET.SubElement(nowele, 'title').text = self.title
        ET.SubElement(nowele, 'link').text = self.link
        ET.SubElement(nowele, 'description').text = self.plantform + self.ep
        return feedsrc

    # 匹配剧集平台

    def recognize(self):
        temp_url = self.url.split("/")[2]
        rec = urlist[temp_url]
        # if rec == 'tencent':
        #     self.tencent()
        # elif rec =='bilibili':
        #     self.bilibili()
        # elif rec==
        self.plantform = rec
        return rec

    # 腾讯视频数据采集
    def tencent(self):
        result = requests.get(self.url).content
        result = bsp(result, 'html5lib')
        self.title = result.head.title.text.split("-")[0]
        result = result.find(attrs={"class": "mod_episode"})
        text = result.text.replace('\t', '').splitlines()
        while '' in text:
            text.remove('')
        contents = result.contents
        for i in contents:
            if type(i) != 'bs4.element.Tag':
                contents.remove(i)
        # if len(text) == len(contents):
        # print(len(text),len(contents))
        num = len(text)
        # print(text,contents)
        text.reverse()
        contents.reverse()
        if text[0].find('展开更多') >= 0:
            self.tencent2()
            return
        else:
            for i in range(num):
                if text[i].isdigit():
                    self.ep = text[i]
                    self.link = contents[i].find('a').get('href')
                    return
        self.tencent2()

    def tencent2(self):
        tempurl = "https://v.qq.com/x/cover/" + self.url.split('/')[5]
        result = requests.get(tempurl).text
        result = list(eval(result.split('\"video_ids\":')[1].split(']')[0] + ']'))
        self.ep = len(result)
        self.link = tempurl[0:-5] + '/' + result[self.ep - 1] + '.html'

    # bilibili数据采集
    def bilibili(self):
        md_id = self.url.split('/')[5].split('md')[1]
        # rubbish way to get title and ep
        try:
            result = requests.get(bilimd, params={'media_id': md_id}).content
        except Exception:
            time.sleep(10)
            result = requests.get(bilimd, params={'media_id': md_id}).content
        result = json.loads(result)['result']['media']
        self.title = result['title']
        self.ep = result['new_ep']['index']
        self.link = biliep + str(result['new_ep']['id'])
        # result = requests.get(biliss,params={'season_id':md_id}).content
        # self.link = json.loads(result)['result']['main_section']['episodes'][int(self.ep) - 1]['share_url']
        print(self.link)
        return

    # bimiacg数据采集
    def bimiacg(self):
        try:
            result = bsp(requests.get(self.url).content, 'html5lib')
        except Exception:
            time.sleep(10)
            result = bsp(requests.get(self.url).content, 'html5lib')
        self.title = result.head.title.text.split('无修版-百度云盘-动漫全集在线观看-bimibimi')[0]
        result = result.find('ul', {"class": "player_list"}).find_all('li')[-1]
        self.ep = result.text
        self.link = bimilink + result.a.get('href')
        return

    def bilimanga(self):
        pass
        return

    def bilichannel(self):
        biliuid, bilicid = self.url.split('/')[3], self.url.split('cid=')[1]
        result = json.loads(requests.get(bilich,
                                         params={'mid': biliuid, 'cid': bilicid}).content)
        result = result['data']['list']['archives'][0]
        self.title = result['title']
        self.ep = result['bvid']
        self.link = "https://bilibili.com/" + self.ep

def main():
    # flag = False
    # updateinfo = None
    with open("list.json", 'r') as file:
        context = json.load(file)
        for i in context['subscribe']:
            newInfo = UpdateInfo(i)
            # print(newInfo.info)
            if i not in context['lastest'] or context['lastest'][i] != newInfo.info:
                context['lastest'][i] = newInfo.info
                try:
                    newInfo.updatefeed(rsstree)
                except:
                    rsstree = ET.parse('feed.xml')
                    rss = rsstree.getroot()
                    rsstree = newInfo.updatefeed(rss)
                # todo
        time.sleep(10)
    file.close()
    try:
        ET.ElementTree(rsstree).write('feed.xml', encoding='utf-8')
        with open("list.json", 'w') as file:
            json.dump(context, file)
        file.close()
    except:
        print('XML file writed Fault!')
    return


if __name__ == '__main__':
    main()
