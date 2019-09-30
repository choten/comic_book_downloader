import re
import requests
from bs4 import BeautifulSoup
import os,json

class Book:
  def __init__(self, href, txt,number):
    self.link = href
    self.title = txt
    self.total_page = number

def get_book_list(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.text,"html.parser") #將網頁資料以html.parser
    sel = soup.select("div #chapterlistload li > a")
    book_list = [ Book("http://www.dm5.com"+s["href"] ,re.sub(r'\s\s','',s.text),10) for s in sel]
    return (book_list)

def download_img(img_url,pic_name):
    pic = requests.get(img_url)
    tmp_img = pic.content
    pic_out = open(pic_name,'wb')
    pic_out.write(tmp_img)
    pic_out.close()

def add_dir(dir_name):
    path = os.path.join(CWD,dir_name)
    if not os.path.isdir(path):
        os.mkdir(path)

CWD = os.path.join(os.getcwd(),"comic book") #資料夾位置

menu_url = "http://www.dm5.com/manhua-zhanguoyaohu/"
book_list = get_book_list(menu_url)
for book in book_list:
    #檢查目錄有沒有此資料夾，若無則新增資料夾    
    # add_dir(book.title)

    count = book.total_page #頁數
    for num in range(count):
        url = book.link + "#ipg"+ str(num+1)
        respond = requests.get(url)
        soup = BeautifulSoup(respond.text,"html.parser")
        # print(soup.prettify())
        sel = soup.select("div #cp_img")
        img_url = sel[0]["src"]

#id="cp_img"



    


