import webbrowser
import requests
from bs4 import BeautifulSoup as bsp
import json
import xml.etree.ElementTree as ET

urlist = {'v.qq.com': 'tencent',
          'www.bilibili.com': 'bilibili',
          'www.bimiacg.com': 'bimiacg',
          }
bilimd = "https://api.bilibili.com/pgc/review/user?media_id="
biliss = "https://api.bilibili.com/pgc/web/season/section?season_id="
bimilink = "https://www.bimiacg.com"


class TencentLenError(Exception):
    def __init__(self, message='text is not as long as contents'):
        super().__init__(message)
        self.message = message

class UpdateInfo:
    # 一步到位，数据采集
    def __init__(self, url):
        self.url = url
        getattr(self, self.recognize())()
        self.info = {"title": self.title,
                     # "plantform": self.plantform,
                     # "episode": self.ep,
                     "link": self.link,
                     "description": self.plantform + self.ep
                     }

    def updatefeed(self, feedsrc):
        feedsrc
        return result

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
        if len(text) == len(contents):
            num = len(text)
            text.reverse()
            contents.reverse()
        else:
            raise TencentLenError()
        # print(type(contents[1]))
        # print(contents)
        for i in range(num):
            # print(bsp(contents[i],'html5lib'))
            # contents[i]=bsp(contents[i],'html5lib').img
            if text[i].isdigit():
                # try:
                #     contents[i].find('img').get('alt')
                # except Exception as e:
                #     print(e)
                self.ep = text[i]
                self.link = contents[i].find('a').get('href')
                return

    # bilibili数据采集
    def bilibili(self):
        md_id = self.url.split('/')[5].split('md')[1]
        result = requests.get(bilimd + md_id).content
        self.title = json.loads(result)['result']['media']['title']
        self.ep = json.loads(result)['result']['media']['new_ep']['index']
        result = requests.get(biliss + md_id).content
        self.link = json.loads(result)['result']['main_section']['episodes'][int(self.ep) - 1]['share_url']
        return

    # bimiacg数据采集
    def bimiacg(self):
        # md_id = self.url.split('/')[5]
        result = bsp(requests.get(self.url).content, 'html5lib')
        self.title = result.head.title.text.split('无修版-百度云盘-动漫全集在线观看-bimibimi')[0]
        result = result.find('ul', {"class": "player_list"}).find_all('li')[-1]
        self.ep = result.text
        self.link = bimilink + result.a.get('href')
        return


if __name__ == '__main__':
    # flag = False
    updateinfo = None
    with open("list.json", 'r') as file:
        context = json.load(file)
        for i in context['subscribe']:
            newInfo = UpdateInfo(i)
            # print(newInfo.info)
            if i not in context['lastest'] or context['lastest'][i] != newInfo.info:
                context['lastest'][i] = newInfo.info
                try:
                    newInfo.updatefeed(feedsrc)
                except:
                    rsstree = ET.parse('test.xml').
                # todo
    file.close()
    if updateinfo is not None:
        with open("list.json", 'w') as file:
            json.dump(context, file)
        file.close()
        # demo = AnalyzeObject(bimidemo)
        # print(demo.ep)
        # demo.full()
        # print(demo.ep,demo.link)
