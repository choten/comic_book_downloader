import re
import requests
from bs4 import BeautifulSoup
import os,json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Book:
  def __init__(self, href, txt,number):
    self.book_url = href
    self.title = txt
    self.total_page = number

def get_book_list(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text,"html.parser") #將網頁資料以html.parser
    sel = soup.select("div #chapterlistload li > a")
    book_list = [ Book("http://www.dm5.com"+s["href"] ,re.sub(r'\s','',s.text),10) for s in sel]
    return (book_list)

def download_img(img_url,pic_path,referer):
    headers = {'referer':referer,'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    pic = requests.get(img_url,headers = headers)
    tmp_img = pic.content
    pic_out = open(pic_path,'wb')
    pic_out.write(tmp_img)
    pic_out.close()

def add_dir(dir_name):
    """
    新增資料夾，資料夾名稱為每集的標題
    """
    path = os.path.join(BOOK_PATH,dir_name)
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

    print(url_list)
    return (url_list)

def download(book_url,dir_path,pag_num):
    WEB.get(book_url)
    #下載漫畫的圖片
    img_url = WEB.find_element_by_id('cp_image').get_attribute("src")
    refer = book_url
    download_img(img_url,os.path.join(dir_path,str(pag_num+2)+'.png'),refer)


def download_comic_book(book_url,dir_path):
    WEB.get(book_url)
    
    #下載漫畫的第一頁圖片
    img_url = WEB.find_element_by_id('cp_image').get_attribute("src")
    refer = book_url
    download_img(img_url,os.path.join(dir_path,'01.png'),refer)
    #下載其他頁的圖片
    total_page = 3
    #取得其他頁數的連結
    url_list = get_url_list(book_url,total_page)

    for pag_num,url in enumerate(url_list):
        download(url,dir_path,pag_num)



CWD = os.getcwd() #程式所在路徑
BOOK_PATH = os.path.join(CWD,"comic book") #漫畫資料夾路徑
chrome_path = os.path.join(CWD,r"selenium_driver_chrome\chromedriver.exe") #chromedriver.exe 執行檔所存在的路徑
path_to_extension = os.path.join(CWD,r'selenium_driver_chrome\3.56.0_0') #adblock 擴充套件路徑
chrome_options = Options()
chrome_options.add_argument('load-extension=' + path_to_extension)    
WEB = webdriver.Chrome(chrome_path,chrome_options=chrome_options)
WEB.create_options()

#menu_url = "http://www.dm5.com/manhua-zhanguoyaohu/"
# menu_url = "http://www.dm5.com/manhua-menjiewaidejinghaizhiwu/"
menu_url = "http://www.dm5.com/manhua-dangxinelingqishi/"
book_list = get_book_list(menu_url)
for book in book_list:
    #檢查目錄有沒有此資料夾，若無則新增資料夾
    dir_path = add_dir(book.title)

    download_comic_book(book.book_url,dir_path)
else:    
    WEB.close()




    


