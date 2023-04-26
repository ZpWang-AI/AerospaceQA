import os
import sys
import time
import traceback

from pathlib import Path as path
from selenium import webdriver
from selenium.webdriver.common.by import By
from msedge.selenium_tools import EdgeOptions, Edge

from utils import *

sys.setrecursionlimit(10**8)


FOLD_SAVED = r"./saved_res"

start_urls = [
    r'https://baike.baidu.com/item/%E8%88%AA%E7%A9%BA%E8%88%AA%E5%A4%A9?fromModule=lemma_search-box',
    
]

mark_file_completed = 'yes.txt'
mark_file_running = 'running.txt'
mark_file_error = 'error.txt'

res_file_url = 'url.txt'
res_file_pagesource = 'page_source.txt'
res_file_links = 'url_links.txt'


def write_txt(file_path, content=''):
    with open(file_path, 'w', encoding='utf-8')as f:
        if type(content) == str:
            f.write(content)
        else:
            for line in content:
                f.write(line+'\n')


class Crawler:
    def __init__(
        self, 
        fold_saved, 
        search_page_per_second=5,
    ) -> None:
        self.driver = None
        
        self._fold_saved = path(fold_saved)
        self._fold_saved.mkdir(parents=True, exist_ok=True)
        self._fold_cnt = 0
        
        self._urls_searched = set()
        for res_fold in os.listdir(self._fold_saved):
            self._fold_cnt = max(self._fold_cnt, int(res_fold)+1)
            res_fold = self._fold_saved/res_fold
            if mark_file_completed in os.listdir(res_fold):
                with open(res_fold/res_file_url, 'r', encoding='utf-8')as f:
                    cur_url = str(f.readline())
                    self._urls_searched.add(cur_url)
        
        self._searching_gap = 1/search_page_per_second
        self._last_search_time = 0
        
        self._urls_wait_list = []
    
    def _start_driver(self):
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_driver_path = 'path/to/chromedriver'

        # # 设置 User-Agent 为 Chrome 浏览器的请求头
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        # chrome_options.add_argument('user-agent={}'.format(user_agent))

        # driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
        self.driver = webdriver.Chrome()
        self.driver.get('https://www.baidu.com/')  # For test
        print('\ndriver works!\n')
        
    def search_urls(self, urls):
        self._start_driver()
        start_time = get_cur_time(return_str=False)
        print(f'\n{get_cur_time()}, start searching\n')

        if type(urls) == str:
            self._urls_wait_list.append(urls)
        else:
            self._urls_wait_list.extend(urls)
            
        while self._urls_wait_list:
            self._search_webpage(self._urls_wait_list.pop())
            
        print(f'\n{get_cur_time()}, finish searching\n'
              f'running time: {get_cur_time(return_str=False)-start_time}\n')
        self.driver.quit()
    
    def _need_search(self):
        return '航天' in self.driver.page_source

    def _fetch_links(self):
        link_elements = self.driver.find_elements(By.TAG_NAME, 'a')
        return [link.get_attribute('href') for link in link_elements]

        # # 遍历每个链接元素，并提取链接地址
        # for link in link_elements:
        #     href = link.get_attribute("href")
        # return []
        
    def _search_webpage(self, webpage):
        if webpage in self._urls_searched:
            return
        self._urls_searched.add(webpage)
        
        time.sleep(max(0, self._last_search_time+self._searching_gap-time.time()))
        self._last_search_time = time.time()

        res_fold = self._fold_saved/str(self._fold_cnt)
        res_fold.mkdir(parents=True, exist_ok=True)
        self._fold_cnt += 1
        write_txt(res_fold/mark_file_running)
        try:
            self.driver.get(webpage)
            print(f'get {webpage}')
            
            if not self._need_search():
                return
            page_source = self.driver.page_source
            new_urls = self._fetch_links()
        except Exception as cur_error:
            write_txt(
                res_fold/mark_file_error,
                [
                    str(cur_error),
                    '-'*20,
                    traceback.format_exc(),
                ]
            )
        else:
            write_txt(res_fold/res_file_url, str(webpage))
            write_txt(res_fold/res_file_pagesource, str(page_source))
            write_txt(res_fold/res_file_links, new_urls)
            self._urls_wait_list.extend(new_urls)
            
            write_txt(res_fold/mark_file_completed)
        finally:
            os.remove(res_fold/mark_file_running)

    
def main():
    crawler = Crawler(
        fold_saved=FOLD_SAVED,
        search_page_per_second=5,
    )
    
    crawler.search_urls(start_urls)
    
    
if __name__ == '__main__':
    main()