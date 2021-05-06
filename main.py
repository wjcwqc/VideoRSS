import requests
from bs4 import BeautifulSoup as bsp
import json
import xml.etree.ElementTree as ET
import time
from retry import retry
import logging
import sys
import addList

urlist = {'v.qq.com': 'tencent',
          'www.bilibili.com': 'bilibili',
          'www.bimiacg.com': 'bimiacg',
          'manga.bilibili.com': 'bilimanga',
          'space.bilibili.com': 'bilichannel'
          }
bilimd = "https://api.bilibili.com/pgc/review/user"
biliss = "https://api.bilibili.com/pgc/web/season/section"
bimilink = "http://www.bimiacg.com"
bilich = "https://api.bilibili.com/x/space/channel/video"
biliep = "https://www.bilibili.com/bangumi/play/ep"


def timeStampExec():
    return str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))


class TencentLenError(Exception):
    def __init__(self, message='text is not as long as contents'):
        super().__init__(message)
        self.message = message


class bimiCopyright(Exception):
    def __init__(self, message='This bimi animation cause a Error'):
        super().__init__(message)
        self.message = message


class UpdateInfo:
    # 一步到位，数据采集
    def __init__(self, url):
        self.url = url
        getattr(self, self.recognize())()
        self.info = {
            'title': self.title,
            'platform': self.platform,
            'episode': self.ep,
            'link': self.link
        }

    # 更新feed文件
    def updatefeed(self, feedsrc):
        nowele = ET.SubElement(feedsrc[0], 'item')
        ET.SubElement(nowele, 'title').text = self.title
        ET.SubElement(nowele, 'link').text = self.link
        ET.SubElement(nowele, 'description').text = self.platform + str(self.ep)
        ET.SubElement(nowele, 'time').text = timeStampExec()
        # print(("[{0}] {1} {2} update success.").format(timeStampExec(), self.title, self.ep))
        logging.debug("{0} {1} update success.".format(self.title, self.ep))
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
        self.platform = rec
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
        num = len(text)
        # 原版采用列表逆序从头查找，现在采用text[-1]和__reversed__方法减少逆序时间
        # text.reverse()
        # contents.reverse()
        if text[-1].find('展开更多') >= 0:
            self.tencent2()
            return
        else:
            for i in range(num).__reversed__():
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
        # print(self.link)
        return

    # bimiacg数据采集
    @retry(bimiCopyright, tries=2)
    def bimiacg(self):
        try:
            result = bsp(requests.get(self.url).content, 'html5lib')
        except:
            time.sleep(10)
            result = bsp(requests.get(self.url).content, 'html5lib')
        # self.title = result.head.title.text.replace('无修版-百度云盘-动漫全集在线观看-bimibimi', '')
        # 上面的标题方法在下面的异常处理后错误所以使用下面方法进行更新
        self.title = result.find_all('strong')[-1].text
        #  print(self.url, result.find('ul', {"class": "player_list"}))
        # 2021.4.17 下面这行出错可能由于，采集页面显示错误导致
        # 处理方法：强制跳转到/paly/1/1进行播放在查询集数
        try:
            result = result.find('ul', {"class": "player_list"}).find_all('li')[-1]
            self.ep = result.text
            self.link = bimilink + str(result.a.get('href'))
            return
        except AttributeError as e:
            self.url = self.url.replace("/bi/", "/") + "play/1/1"
            logging.debug("{0} cause a Copyright block! details:{1}".format(self.link, e))
            raise bimiCopyright

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

    logging.basicConfig(filename='VideoRSS.log',
                        format="[%(asctime)s]%(levelname)s:%(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        )
    logging.debug("Update start!")
    # logger.setLevel(logging.ERROR)
    with open("list.json", 'r') as file:
        context = json.load(file)
        for i in context['subscribe']:
            logging.debug(i + "start")
            newInfo = UpdateInfo(i)
            # print(newInfo.info)
            if i not in context['lastest'] or context['lastest'][i] != newInfo.info:
                context['lastest'][i] = newInfo.info
                try:
                    newInfo.updatefeed(rsstree)
                except:
                    # print(("[{0}] {1} update failed.").format(timeStampExec(), i))
                    logging.warning(i + " update failed.")
                    rsstree = ET.parse('feed.xml')
                    rss = rsstree.getroot()
                    rsstree = newInfo.updatefeed(rss)
    file.close()
    try:
        ET.ElementTree(rsstree).write('feed.xml', encoding='utf-8')
        with open("list.json", 'w') as file:
            json.dump(context, file, indent=4)
        file.close()
        # print('[' + timeStampExec() + '] XML file update success!')
        logging.debug("XML file update success!")
    except:
        # print('[' + timeStampExec() + '] XML file update failed or nothing need to be updated!')
        logging.info("XML file update failed or nothing need to be updated!")
    return


if __name__ == '__main__':
    if sys.argv != None:
        try:
            tup = sys.argv[1:]
            addList.add(tup)
        except Exception as e:
            print(sys.argv)
    main()
