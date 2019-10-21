import re
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
from opencc import OpenCC
import timeit
from showprocess import ShowProcess
import math

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
    chrome_options.add_argument('--ignore-certificate-errors')
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager" 
    browser = webdriver.Chrome(chrome_path,options=chrome_options,desired_capabilities=caps)
    browser.set_window_size(100,100)
    return (browser)

def crawl_menu_page(WEB,book_path,menu_url):
    """
    爬 menu 網頁，抓取標題、封面、每集volume的url，並回傳 (漫畫路徑,volumes列表)
    """
    html = requests.get(menu_url)
    soup = BeautifulSoup(html.text,"html.parser") #將網頁資料以html.parser
    # print(html.text)

    #取得漫畫 title
    p_tag = soup.select_one("div.banner_detail_form > div.info > p.title")
    title = re.sub(r'\s|(\d{1,2}\.\d{0,1}分)','',p_tag.text)
    title = convert_s2t(title)

    #新增 [漫畫名稱]資料夾
    book_path = create_directory(book_path,title)

    #下載封面 img
    img_tag = soup.select_one("section.banner_detail > div.banner_border_bg > img.banner_detail_bg")
    cover_url = img_tag['src']
    pic_path = os.path.join(book_path,'封面.png')
    referer = menu_url
    download_img(cover_url,pic_path,referer)

    #取得 volumes 連結
    a_tags = soup.select("div #chapterlistload li > a")
    if len(a_tags) <= 0 :
        #代表menu頁的子連結為ajax 產生，得用 Selenium 來抓
        WEB.get(menu_url)
        a_tags = WEB.find_elements_by_css_selector(("#chapterlistload > li > a"))
        
        assert len(a_tags) > 0,"無法取得每集的連結"
        #部分隱藏起來的連結的txt為空，會造成名稱取值的問題



    volume_list = [ Volume(ROOT_URL+a_tag["href"] ,trim(a_tag.text),extract_total_page(a_tag.text)) for a_tag in a_tags]

    return (book_path,volume_list)

def download_volume(browser,TAB_LIST,book_url,dir_path,total_page):
    """
    下載這集的漫畫
    """
    browser.get(book_url)
    
    #下載第一頁的圖片
    img_url = browser.find_element_by_id('cp_image').get_attribute("src")
    refer = book_url
    pic_path = os.path.join(dir_path,'1.png')
    download_img(img_url,pic_path,refer)
    PROCESS_BAR.show_process()
    
    #取得其他頁數的連結
    url_list = create_page_url_list(book_url,total_page)

    #下載其他頁的圖片
    # for pag_num,url in enumerate(url_list):
    #     crawl_book_page(browser,url,dir_path,pag_num)
    #     PROCESS_BAR.show_process()

    tab_len = len(TAB_LIST)
    m = math.ceil(len(url_list)/tab_len) + 1
    for i in range(m):
        for j in range(tab_len):
            current_page = tab_len*i+j
            if current_page >= len(url_list) + tab_len:
                break

            browser.switch_to.window(TAB_LIST[j])

            if i != 0: #第一輪不下載
                pag_num = current_page - tab_len
                crawl_img(browser,book_url,dir_path,pag_num)
                PROCESS_BAR.show_process() 

            if current_page < len(url_list):
                browser.get(url_list[current_page])


def crawl_img(browser,book_url,dir_path,pag_num):
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "cp_image"))
        )
        #下載漫畫的圖片
        img_url = browser.find_element_by_id('cp_image').get_attribute("src")
        refer = book_url
        download_img(img_url,os.path.join(dir_path,str(pag_num+2)+'.png'),refer)
    except:
        print(book_url+'下載失敗')

# def crawl_book_page(browser,book_url,dir_path,pag_num):
#     """
#     前往 url 網址，爬取圖片的 url 並下載 
#     """
#     browser.get(book_url)
#     try:
#         WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.ID, "cp_image"))
#         )
#         #下載漫畫的圖片
#         img_url = browser.find_element_by_id('cp_image').get_attribute("src")
#         refer = book_url
#         download_img(img_url,os.path.join(dir_path,str(pag_num+2)+'.png'),refer)
#     except:
#         print(book_url+'下載失敗')

def create_page_url_list(book_url,total_page):
    """
    製造其他頁數的連結
    """    
    # 轉換範例:
    # 'http://www.dm5.com/m907153/' -> 'http://www.dm5.com/m907153-p'
    url_template = re.sub(r'/$','-p',book_url)
    url_list = [url_template + str(num+2) for num in range(total_page-1)]

    return (url_list)

def download_img(img_url,pic_path,referer):
    """
    下載圖片，referer : 當前網頁的url，requset 時要放在 header
    """
    headers = {'referer':referer,'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    pic = requests.get(img_url,headers = headers)
    tmp_img = pic.content
    pic_out = open(pic_path,'wb')
    pic_out.write(tmp_img)
    pic_out.close()

def create_directory(book_path,dir_name):
    """
    檢查book_path 之下有沒有此 [dir_name] 資料夾，若無則新增，並回傳新增後的路徑
    """
    path = os.path.join(book_path,dir_name)
    if not os.path.isdir(path):
        os.mkdir(path)

    return (path)

def trim(str_input):
    """
    去除空白字元，並且簡體轉繁體
    """
    trimed_input = re.sub(r'\s','',str_input)
    str_output = convert_s2t(trimed_input)
    return (str_output)

def extract_total_page(str_title):
    """
    從漫畫標題擷取出總頁數
    """
    totalPage = int(re.findall(r'（(\d{1,3})P）|$',str_title)[0])
    return (totalPage)

def convert_s2t(str_input):
    """
    簡轉繁，並轉換大陸用語為台灣用語
    """
    cc = OpenCC('s2twp') #設定簡轉繁，並轉換大陸用語為台灣用語
    str_output = cc.convert(str_input)
    return (str_output)

def is_menu_url_valid(menu_url):
    """
    驗證 menu url 格式是否正確
    """
    pattern  = re.compile(r'^http://www\.dm5\.com/manhua-([a-z]|-)+/?$')
    result = pattern.fullmatch(menu_url)
    if result == None:
        return False
    else:
        return True

def sum_total_step(volume_list):
    """
    計算漫畫總張數，給進度條計算用
    """
    total_stap = 0
    for book in volume_list:
        total_stap += book.total_page
    return (total_stap)

def app_start():
    """
    程式起始點
    """
    book_path = os.path.join(CURRENT_DIR,"comic book") #漫畫資料夾路徑
    # menu_url = input("請輸入漫畫網址:\n")
    menu_url = 'http://www.dm5.com/manhua-dangxinelingqishi/'
    
    while is_menu_url_valid(menu_url) == False:
        print("失敗! 漫畫網址格式錯誤，請重新輸入")
        menu_url = input("請輸入漫畫網址:\n")

    #初始化 web driver
    browser = init_web_driver()
    browser.create_options()

    #多開三個分頁，共五個分頁
    for _ in range(3):
        browser.execute_script("window.open('about:blank');")

    TAB_LIST = browser.window_handles
    browser.switch_to.window(TAB_LIST[0])
    # browser.minimize_window()

    result = crawl_menu_page(browser,book_path,menu_url)
    book_path = result[0]
    volume_list = result[1]
    volume_list.reverse()

    #初始化進度條物件參數
    max_steps = sum_total_step(volume_list)
    PROCESS_BAR.max_steps = max_steps
    PROCESS_BAR.infoDone += book_path
    print("下載進度")
    PROCESS_BAR.show_process(0)
    
    for book in volume_list:
        #檢查目錄有沒有此資料夾，若無則新增資料夾
        dir_path = create_directory(book_path,book.title)

        download_volume(browser,TAB_LIST,book.book_url,dir_path,book.total_page)
    else:    
        browser.quit()

def test():
    """
    測試程式碼
    """
    t = timeit.timeit(stmt="app_start()", setup="from  __main__ import app_start", number=1)
    print(t)

if __name__=='__main__':
    CURRENT_DIR = os.getcwd() #程式所在路徑
    ROOT_URL = "http://www.dm5.com" #網頁的根目錄
    infoDone = '下載完成!\n 漫畫存放位置: \n'
    PROCESS_BAR = ShowProcess(10,infoDone)

    try:
        # app_start()
        test()
    except Exception as e:
        print("下載失敗")
        print(e)
        input() 