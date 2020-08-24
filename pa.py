"""
Han Tmooc
"""
import struct
import time
import requests
from lxml import etree
from Crypto.Cipher import AES
from queue import Queue
import re
import os
from threading import Thread
class DaiNeiVideoSpider:
    def __init__(self):
        self.url='http://tts.tmooc.cn/studentCenter/toMyttsPage'
        self.headers = {
            'Cookie':'isCenterCookie=no; ssss768803=0; ssss779973=0; tedu.local.language=zh-CN; __root_domain_v=.tmooc.cn; _qddaz=QD.rwf95u.l864tk.ka0g2ska; Hm_lvt_51179c297feac072ee8d3f66a55aa1bd=1595554545,1595570953,1595574051,1595900797; TMOOC-SESSION=01691b32d8224f47ab11c337bbf18d85; _qddab=3-4zigpm.kd6q8bsq; Hm_lpvt_51179c297feac072ee8d3f66a55aa1bd=1596021208; sessionid=01691b32d8224f47ab11c337bbf18d85|E_bfusn2b; cloudAuthorityCookie=0; versionListCookie=AIDTN202004; defaultVersionCookie=AIDTN202004; versionAndNamesListCookie=AIDTN202004N22NPython%25E4%25BA%25BA%25E5%25B7%25A5%25E6%2599%25BA%25E8%2583%25BD%25E5%2585%25A8%25E6%2597%25A5%25E5%2588%25B6%25E8%25AF%25BE%25E7%25A8%258BV08N22N779973; courseCookie=AID; stuClaIdCookie=779973; JSESSIONID=58AB0BF6873684BEF4CD6CA2ACC7FC5A; Hm_lvt_e997f0189b675e95bb22e0f8e2b5fa74=1595900835,1595985002,1595985908,1596021214; Hm_lpvt_e997f0189b675e95bb22e0f8e2b5fa74=1596021214',
            'Referer': 'http://uc.tmooc.cn/userCenter/toUserCoursePage',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
        self.queue=Queue()
        self.dir=r'G:\Programs\TTS\video'  #如需修改视频存放位置可修改此处
    def parse_one(self):
        print("正在加载m3u8链接...")
        video_list=[]
        html = requests.get(url=self.url, headers=self.headers).content.decode('utf-8')
        parse_html = etree.HTML(html)
        link_list = parse_html.xpath('//li[@class="sp"]/a/@href')
        # print(link_list)
        # print(len(link_list))
        for video in link_list:
            video_list.append(video)
            # print(video_list)
        return video_list
    # 解析二级界面从二级界面中找出m3u8链接
    def parse_two(self,video_list):
        m3u8_list=[]
        for url in video_list:
            # print(link_list)
            # print(len(link_list))
            html=requests.get(url=url,headers=self.headers).content.decode('utf-8')
            parse_html = etree.HTML(html)
            # 每天上午  下午链接
            link_list01 = parse_html.xpath('//div[@class="video-list"]//p/@id')
            if len(link_list01)==0:
                pass
            # print(link_list01)
            for item in link_list01:
                # print(item)
                a=item.split('_')
                last_url01 = a[1:]
                last_url='_'.join(last_url01)
                middle_url = last_url.split('.')[0]
                # print(middle_url)
                m3u8_url = 'http://c.it211.com.cn/' + middle_url + '/' + last_url
                m3u8_list.append(m3u8_url)

        print(m3u8_list)
        print(len(m3u8_list))
        print("m3u8链接加载完毕...")
        return m3u8_list

    def insert_queue(self,m3u8_list):
        for m3u8 in m3u8_list:
            self.queue.put(m3u8)
        return self.queue

    def parse_m3u8(self,m3u8_url):

        ts_list = []
        print(m3u8_url)
        file=m3u8_url.split('/')[-1]
        dic_name=file.split('.')[0]
        # html=requests.get(url=m3u8_url,headers=self.headers)
        # print(html)
        # if html.status_code==404:
        #     print('url或视频出现错误,跳过')
        #     pass
        # # print(html)
        # else:
        html = requests.get(url=m3u8_url, headers=self.headers).text
        # print(html)
        parse_key = re.compile('URI="(.*?)"', re.S)
        key01 = parse_key.findall(html)
        if len(key01)==0:
            print("{}该视频无法正常播放".format(m3u8_url))
            # with open("/home/ren/video/播放错误url.txt",'a+') as f:
            with open(self.dir+"播放错误url.txt",'a+') as f:
                f.write("{}无法正常播放".format(m3u8_url))
            pass
        else:
            key=key01[0]
            print(key)
            list01 = html.split('\n')
            for item in list01:
                if '.ts' in item:
                    ts_list.append(item)

            print(ts_list)
            self.write(key,dic_name,ts_list)
    #
    def write(self,key,dic_name,ts_list):
        # pass
        keys = requests.get(url=key, headers=self.headers).content
        # 创建文件夹用来存放每半天的视频
        dir = self.dir+'{}'.format(dic_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
            print('{}文件夹创建成功'.format(dic_name))

            with open('{}/{}.mp4'.format(dir, dic_name), 'ab') as f:
                for url in ts_list:
                    res=requests.get(url=url,headers=self.headers).content
                    file_name01=url.split('-')[-1]
                    file_name02=file_name01.split('.')[0]
                    cryptor = AES.new(keys, AES.MODE_CBC, keys)
                    f.write(cryptor.decrypt(res))
                    print('{}写入成功'.format(file_name02))
        else:
            ts_list.clear()
            print("{}文件夹已存在，请确认文件是否爬取完毕，如未爬取完毕请删除此文件夹".format(dic_name))
            pass

    def main(self):
        thread_list=[]
        video_list=self.parse_one()
        m3u8_list=self.parse_two(video_list)
        queue=self.insert_queue(m3u8_list)
        while not queue.empty():
            for i in range(2):
                if not queue.empty():
                    m3u8_url=queue.get()
                    print(m3u8_url)
                    thread=Thread(target=self.parse_m3u8,args=(m3u8_url,))
                    thread.start()
                    print(thread.getName()+"启动成功")
                    time.sleep(0.5)
                    thread_list.append(thread)

                else:
                    break
            for k in thread_list:
                k.join()
                thread_list.remove(k)
                print(k.getName()+"回收成功")
if __name__=='__main__':
    spider=DaiNeiVideoSpider()
    spider.main()

