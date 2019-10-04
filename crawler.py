import re
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Volume:
    """
    漫畫物件
    """
    def __init__(self, href, txt,total_page):
        self.book_url = href
        self.title = txt
        self.total_page = total_page

def init_web_driver():
    """
    初始化 web driver
    """    
    chrome_path = os.path.join(CURRENT_DIR,r"selenium_driver_chrome\chromedriver.exe") #chromedriver.exe 執行檔所存在的路徑
    path_to_extension = os.path.join(CURRENT_DIR,r'selenium_driver_chrome\3.56.0_0') #adblock 擴充套件路徑
    chrome_options = Options()
    chrome_options.add_argument('load-extension=' + path_to_extension)    
    WEB = webdriver.Chrome(chrome_path,options=chrome_options)
    return (WEB)
    

def get_book_list(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text,"html.parser") #將網頁資料以html.parser
    sel = soup.select("div #chapterlistload li > a")
    book_list = [ Volume("http://www.dm5.com"+s["href"] ,re.sub(r'\s','',s.text),10) for s in sel]
    return (book_list)

def download_img(img_url,pic_path,referer):
    headers = {'referer':referer,'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    pic = requests.get(img_url,headers = headers)
    tmp_img = pic.content
    pic_out = open(pic_path,'wb')
    pic_out.write(tmp_img)
    pic_out.close()

def create_directory(book_path,dir_name):
    """
    檢查book_path 之下有沒有[dir_name]資料夾，若無則新增，並回傳新增後的路徑
    """
    path = os.path.join(book_path,dir_name)
    if not os.path.isdir(path):
        os.mkdir(path)

    return (path)

def get_url_list(book_url,total_page):
    """
    製造其他頁數的連結
    return url_list
    """    
    # "http://www.dm5.com/m907153/' -> 'http://www.dm5.com/m907153-p'
    url_template = re.sub(r'/$','-p',book_url)
    url_list = [url_template + str(num+2) for num in range(total_page-1)]

    return (url_list)

def download(book_url,dir_path,pag_num):
    WEB.get(book_url)
    #下載漫畫的圖片
    img_url = WEB.find_element_by_id('cp_image').get_attribute("src")
    refer = book_url
    download_img(img_url,os.path.join(dir_path,str(pag_num+2)+'.png'),refer)


def download_comic_book(book_url,dir_path,total_page):
    WEB.get(book_url)
    
    #下載漫畫的第一頁圖片
    img_url = WEB.find_element_by_id('cp_image').get_attribute("src")
    refer = book_url
    pic_path = os.path.join(dir_path,'01.png')
    download_img(img_url,pic_path,refer)
    #下載其他頁的圖片
    # total_page = 3
    #取得其他頁數的連結
    url_list = get_url_list(book_url,total_page)

    for pag_num,url in enumerate(url_list):
        download(url,dir_path,pag_num)


CURRENT_DIR = os.getcwd() #程式所在路徑
#初始化 web driver
WEB = init_web_driver()
WEB.create_options()

BOOK_PATH = os.path.join(CURRENT_DIR,"comic book") #漫畫資料夾路徑
menu_url = "http://www.dm5.com/manhua-dangxinelingqishi/"
# book_list = get_book_list(menu_url)
html = requests.get(menu_url)
soup = BeautifulSoup(html.text,"html.parser") #將網頁資料以html.parser

#取得漫畫 title
p_tag = soup.select_one("div.banner_detail_form > div.info > p.title")
title = re.sub(r'\s|(\d{1,2}\.\d{0,1}分)','',p_tag.text)

#新增 [漫畫名稱]資料夾
BOOK_PATH = create_directory(BOOK_PATH,title)

#下載封面 img
img_tag = soup.select_one("section.banner_detail > div.banner_border_bg > img.banner_detail_bg")
cover_url = img_tag['src']
pic_path = os.path.join(BOOK_PATH,'封面.png')
referer = menu_url
download_img(cover_url,pic_path,referer)

#取得 volumes 連結
a_tags = soup.select("div #chapterlistload li > a")
volume_list = [ Volume("http://www.dm5.com"+a_tag["href"] ,re.sub(r'\s','',a_tag.text),int(re.findall(r'（(\d{1,3})P）|$',a_tag.text)[0])) for a_tag in a_tags]

for book in volume_list:
    #檢查目錄有沒有此資料夾，若無則新增資料夾
    dir_path = create_directory(BOOK_PATH,book.title)

    download_comic_book(book.book_url,dir_path,book.total_page)
else:    
    WEB.close()




    


