import urllib
import re
from html.parser import HTMLParser
from urllib import request
from urllib.request import urlretrieve
import execjs
import requests
import urllib.parse
import os

chapter_list=[]
chapter_count=-1
folder_path='./image/'

def get_html(url):
    # page = request.urlopen(url)
    # html = page.read()
    # #print (html)
    # return html

    

    req = urllib.request.Request(url)
    #模拟Mozilla浏览器进行爬虫
    req.add_header("user-agent","Mozilla/5.0")
    response2 = urllib.request.urlopen(req)
    #print (response2.read())

    return response2.read()


def urllib_download(pic_url,pic_path):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    urlretrieve(pic_url, pic_path) 

class parser_pic(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.flag=0
    
    #<a href="/m128587/" class="detail-list-form-item  " title="" target="_blank">周刊184                     <span>（21P）</span>                                </a>

    def handle_starttag(self,tag,attrs):
        global chapter_list
        global chapter_count

        if (tag=='a' and attrs.__contains__(('class','detail-list-form-item  '))) or (tag=='a' and attrs.__contains__(('class','detail-list-form-item  hide'))):
            self.flag=1
            chapter_count=chapter_count+1
            chapter_list.append(dict())
            # print(type(chapter_list[chapter_count]))
            # print(chapter_list[chapter_count])
            # print(type(attrs))
            # print(attrs)

            for i in attrs:
                if i[0]=='href':
                    chapter_list[chapter_count]['href']=i[1]

    def handle_data(self, data):
        global chapter_list
        global chapter_count

        if self.flag==1:
            chapter_list[chapter_count]['title']=data.strip()
        
        self.flag=0

class Mangabz:
    """
    日本漫画漫画章节图片下载
    """
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                        "Referer": self.url,
                        "Cookie": "image_time_cookie=17115|637270678077155170|2",
                        }

    def get_chapter_argv(self):
        res = requests.get(self.url, headers=self.headers, timeout=10)
        mangabz_cid = re.findall("MANGABZ_CID=(.*?);", res.text)[0]
        mangabz_mid = re.findall("MANGABZ_MID=(.*?);", res.text)[0]
        page_total = re.findall("MANGABZ_IMAGE_COUNT=(.*?);", res.text)[0]
        mangabz_viewsign_dt = re.findall("MANGABZ_VIEWSIGN_DT=\"(.*?)\";", res.text)[0]
        mangabz_viewsign = re.findall("MANGABZ_VIEWSIGN=\"(.*?)\";", res.text)[0]
        return (mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total)

    def get_images_js(self, page, mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign):
        url = self.url + "chapterimage.ashx?" + "cid=%s&page=%s&key=&_cid=%s&_mid=%s&_dt=%s&_sign=%s" % (mangabz_cid, page, mangabz_cid, mangabz_mid, urllib.parse.quote(mangabz_viewsign_dt), mangabz_viewsign)
        res = self.session.get(url, headers=self.headers, timeout=10)
        self.headers["Referer"] = res.url
        return res.text

    def run(self):
        mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total = self.get_chapter_argv()

        for i in range(int(page_total)):
            i += 1
            js_str = self.get_images_js(i, mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign)
            imagesList = execjs.eval(js_str)
            
            #print(imagesList[0])
            print("downloading page "+str(i)+' '+'total '+str(page_total)+'...')
            
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            download_path=folder_path+str(i)+'.jpg'

            if not os.path.exists(download_path):
                urllib_download(imagesList[0],download_path)
            else:
                print(download_path+' exists!')




parser=parser_pic()
html_page = get_html('http://www.mangabz.com/60bz/').decode('utf-8')
parser.feed(html_page)


#{'href': '/m9385/', 'title': '第1卷'}
if not os.path.exists('./download/'):
    os.mkdir('./download/')

for i in chapter_list:
    print(i['title'])

    target_url="http://www.mangabz.com/"+i['href']
    folder_path='./download/'+i['title']+'/'

    mangabz = Mangabz(target_url)
    mangabz.run()




