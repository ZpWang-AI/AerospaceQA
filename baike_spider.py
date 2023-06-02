import re
import requests
import random
import time
import json
import sys
import os
import traceback

from bs4 import BeautifulSoup
from tqdm import tqdm
from requests.exceptions import ProxyError

from utils import sleep_random_time, get_cur_time, exception_handling
from proxy_utils import get_proxy
from data_utils import load_data, dump_data
from keyword_extraction import KeywordManager
from settings import (BAIKE_ALL_INFO_FILE,
                      BAIKE_CRAWLED_FILE,
                      BAIKE_NOT_FOUND_FILE,
                      BAIKE_LOG_FILE,
                      BAIKE_ERROR_FILE,
                      PROXY_URL,
                      )


url_prefix = " https://baike.baidu.com/item/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def log_info(*args, sep=' '):
    info = sep.join(args)
    print(info)
    dump_data(BAIKE_LOG_FILE, info, mode='a')
    

class BaikeSpider():
    def __init__(self, 
                 retry_time=3, 
                 proxy_url=None, 
                 sleep_time=2.5, 
                 only_abstrct=False,
                 save_res=True,
                 ) -> None:
        self._retry_time = retry_time
        self._proxy_url = proxy_url
        self._sleep_time = sleep_time
        self._only_abstract = only_abstrct
        self._save_res = save_res
        
        self._crawled = [line['keyword']for line in load_data(BAIKE_CRAWLED_FILE, default=())]
        self._crawled = set(self._crawled)
        self._not_found = load_data(BAIKE_NOT_FOUND_FILE, default=())
        self._not_found = set(self._not_found)
        
    def _deal_piece(self, keyword, url, soup):
        title = soup.find('h1').get_text()
        main_content = soup.find('div', class_='main-content').get_text().replace('\n', ' ').replace('\xa0', ' ')
        main_content = re.sub(r'收藏查看我的收藏\d*有用\+\d*已投票\d*', '', main_content)
        main_content = re.sub(r'\[\d*\]', '', main_content)
        
        links = []
        filter_list = ['秒懂本尊答', '秒懂大师说', '秒懂看瓦特', '秒懂五千年', '秒懂全视界', '百科热词团队']
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'item' in href:
                for filter_word in filter_list:
                    if filter_word in href:
                        break
                else:
                    links.append("https://baike.baidu.com" + href)

        data_piece = {
            "keyword": keyword, 
            "url": url,
            "title": title,
            "content": main_content,
            "linked_links:": links,
        }
        return data_piece
    
    def _crawl_one_piece(self, keyword):
        if keyword in self._crawled or keyword in self._not_found:
            log_info(keyword + " has benn crawled already.")
            return
        
        url = url_prefix+keyword
        response = requests.get(
            url=url, 
            headers=headers, 
            proxies=get_proxy(proxy_url=self._proxy_url, return_str=False),
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='main-content')
        if content is None:
            self._not_found.add(keyword)
            if self._save_res:
                dump_data(BAIKE_NOT_FOUND_FILE, keyword, mode='a')
            # log_info(keyword + " not found in Baidu Baike")
        else:
            self._crawled.add(keyword)
            data_piece = self._deal_piece(keyword, url, soup)
            if self._save_res:
                dump_data(BAIKE_ALL_INFO_FILE, data_piece, mode='a')
            crawled_piece = {'keyword': keyword, 'url': url}
            if self._save_res:
                dump_data(BAIKE_CRAWLED_FILE, crawled_piece, mode='a')
            # log_info(keyword + " found in Baidu Baike, now crawling...")

        sleep_random_time(self._sleep_time)
    
    def crawl_keywords(self, keyword_list):
        start_log = f"\n{'*'*10}\n{get_cur_time()}\n{'*'*10}"
        log_info(start_log)
        
        keyword_list = set(keyword_list)
        todo_keywords = keyword_list-self._crawled-self._not_found
        for keyword in tqdm(sorted(todo_keywords), desc='baike'):
            exception_handling(
                target_func=lambda:self._crawl_one_piece(keyword),
                display_message=keyword,
                error_file=BAIKE_ERROR_FILE,
                error_return=None,
                exception_handle_methods=(
                    [ProxyError, lambda:sleep_random_time(self._sleep_time)],
                ),
                retry_time=self._retry_time,
                sleep_time=self._sleep_time,
            )


def main_baike():
    total_keywords = KeywordManager.get_total_keywords()
    baike_spider = BaikeSpider(
        retry_time=3,
        proxy_url=PROXY_URL,
        sleep_time=2.5,
        only_abstrct=False,
        save_res=True,
    )
    baike_spider.crawl_keywords(total_keywords)
   
   
if __name__ == '__main__':
    main_baike()