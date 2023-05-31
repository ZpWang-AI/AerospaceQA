# utf-8
import requests
import re
import string
import random
import time
import os
import json
import zhidao_norm as zhidao_norm
import traceback

from tqdm import tqdm
from lxml import etree
from collections import OrderedDict
from baiduspider import BaiduSpider

from utils import sleep_random_time, get_cur_time
from proxy_utils import get_proxy
from data_utils import load_data, dump_data
from keyword_extraction import KeywordManager
from zhidao_norm import Normalizer
from settings import (ZHIDAO_ALL_INFO_FILE,
                      ZHIDAO_CRAWLED_FILE,
                      ZHIDAO_NOT_FOUND_FILE,
                      ZHIDAO_LOG_FILE,
                      ZHIDAO_ERROR_FILE,
                      PROXY_URL,
                      )

spider = BaiduSpider()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

not_found_word_file = ZHIDAO_NOT_FOUND_FILE
crawled_file = ZHIDAO_CRAWLED_FILE
all_info_file = ZHIDAO_ALL_INFO_FILE


def log_info(*args, sep=' '):
    info = sep.join(args)
    print(info)
    dump_data(ZHIDAO_LOG_FILE, info, mode='a')


class Zhidao_spider:
    def __init__(self, 
                 page_size=2, 
                 retry_time=3, 
                 proxy_url=None, 
                 sleep_time=2.5, 
                 save_res=True,
                 ):
        self._page_size = page_size
        self._retry_time = retry_time
        self._proxy_url = proxy_url
        self._sleep_time = sleep_time
        self._save_res = save_res

        self._normalizer = Normalizer()

        if ZHIDAO_CRAWLED_FILE.exists():
            self._key_dic = load_data(ZHIDAO_CRAWLED_FILE)
            self._url_dic = {}
            for key, url_lst in self._key_dic.items():
                for url in url_lst: 
                   self._url_dic[url] = key
        else:
            self._key_dic = {}
            self._url_dic = {}
        if ZHIDAO_NOT_FOUND_FILE.exists():
            self._not_found = load_data(ZHIDAO_NOT_FOUND_FILE)
            self._not_found = set(self._not_found)
        else:
            self._not_found = set()
    
    def _crawl_urls(self, keyword):
        print("{} Crawl URLS...".format(keyword))
        urls = set()
        for page in range(1, self._page_size+1):
            try:
                res_lst = spider.search_zhidao(keyword+' 百度知道', pn=page).plain
            except BaseException as err:
                es = '\n'.join(map(str, [
                    '=='*10,
                    keyword,
                    '-'*10,
                    traceback.format_exc(),
                    f'>> error {str(err)} <<',
                    '-'*10,
                ]))
                log_info(es)
                dump_data(ZHIDAO_ERROR_FILE, es)
            
            for result in res_lst:
                url = result['url']
                if url not in self._url_dic:
                    urls.add(result['url'])
        return urls

    def _crawl_answers(self, url):
        response = requests.get(
            url, 
            headers=headers, 
            proxies=get_proxy(proxy_url=self._proxy_url, return_str=False)
        )
        if response is None:
            return ([]for _ in range(4))
            
        # response.encoding = 'gb1213'
        html = etree.HTML(response.text)
        title = html.xpath('//*[@id="wgt-ask"]/h1/span//text()')
        best_answer = html.xpath('//div[@class="best-text mb-10 dd"]//text()')
        if not best_answer: best_answer = html.xpath('//div[@class="best-text mb-10"]//text()')
        other_answers = html.xpath('//div[@class="answer-text mb-10"]//text()') 
        if not other_answers: other_answers = html.xpath('//div[@class="answer-text mb-10 line"]//text()')
        links = html.xpath('//*[@id="wgt-related"]/div[1]/ul//a/@href')

        return title, best_answer, other_answers, links
    
    def _crawl_one_url(self, keyword, url):
        title, best_answer, other_answers, links = self._crawl_answers(url)
        links = [url+link for link in links]
        if not (best_answer or other_answers):
            return
        
        title = self._normalizer.cleaner(''.join(title).strip())
        best_answer = self._normalizer.cleaner(''.join(best_answer).strip())
        other_answers = self._normalizer.cleaner(''.join(other_answers).strip())
            
        crawled_content = {
            'keyword':keyword, 
            'url':url, 
            'title':title, 
            'content1':best_answer,
            'content2':other_answers, 
            'related_links':links, 
            'last_time':time.asctime(),
        }
            
        if keyword not in self._key_dic:
            self._key_dic[keyword] = []
        self._key_dic[keyword].append(url)
        self._url_dic[url] = keyword
        if self._save_res:
            dump_data(ZHIDAO_ALL_INFO_FILE, crawled_content, mode='a')
            with open(ZHIDAO_CRAWLED_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._key_dic, f, indent=4, ensure_ascii=False)
            
    def _crawl_one_keyword(self, keyword):
        if keyword in self._key_dic:
            print(f"{keyword} zhidao has been crawled already.")
            return

        urls = self._crawl_urls(keyword)
        for url in tqdm(urls, desc=keyword):
            retry_cnt = 0
            while 1:
                retry_cnt += 1
                try:
                    self._crawl_one_url(url)
                    break
                except BaseException as err:
                    if retry_cnt == 1:
                        es = '\n'.join(['=='*10, keyword, '-'*10])
                        log_info(es)
                        dump_data(ZHIDAO_ERROR_FILE, es)
                    es = '\n'.join(map(str, [
                        traceback.format_exc(),
                        f'>> retry {retry_cnt} <<',
                        f'>> error {str(err)} <<',
                        '-'*10
                    ]))
                    log_info(es)
                    dump_data(ZHIDAO_ERROR_FILE, es)
                    if retry_cnt == self._retry_time:
                        break
                    else:
                        sleep_random_time(self._sleep_time)

        sleep_random_time(self._sleep_time)

    def crawl_keywords(self, keyword_list):
        start_log = f"\n{'*'*10}\n{get_cur_time()}\n{'*'*10}"
        log_info(start_log)
        
        keyword_list = set(keyword_list)
        todo_keywords = keyword_list-set(self._key_dic.keys())
        for keyword in tqdm(sorted(todo_keywords)):
            self._crawl_one_keyword(keyword)
                        
       
def main_zhidao():
    total_keywords = KeywordManager.get_all_keywords()
    zhidao_spider = Zhidao_spider(
        page_size=2,
        retry_time=3,
        proxy_url=PROXY_URL,
        sleep_time=2.5,
        save_res=False,
    )
    zhidao_spider.crawl_keywords(total_keywords)
    
            
if __name__ == '__main__':
    main_zhidao()


