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
import warnings

from tqdm import tqdm
from lxml import etree
from collections import OrderedDict
from baiduspider import BaiduSpider

from utils import sleep_random_time, get_cur_time, exception_handling
from proxy_utils import get_proxy
from data_utils import load_data, dump_data
from keyword_extraction import KeywordManager
from zhidao_norm import Normalizer
from settings import (ZHIDAO_ALL_INFO_FILE,
                      ZHIDAO_CRAWLED_KEYWORD_FILE,
                      ZHIDAO_CRAWLED_URL_FILE,
                      ZHIDAO_LOG_FILE,
                      ZHIDAO_ERROR_FILE,
                      PROXY_URL,
                      )

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def log_info(*args, sep=' '):
    info = sep.join(args)
    print(info)
    dump_data(ZHIDAO_LOG_FILE, info, mode='a')


class ZhidaoSpider:
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

        self._spider = BaiduSpider()
        self._normalizer = Normalizer()
    
        self._key_dic = load_data(ZHIDAO_CRAWLED_KEYWORD_FILE, default={})
        self._url_set = set(load_data(ZHIDAO_CRAWLED_URL_FILE, default=()))
            
    def _crawl_urls(self, keyword):
        # log_info("{} Crawling ...".format(keyword))
        urls = set()
        for page in range(1, self._page_size+1):
            res_lst = exception_handling(
                target_func=lambda:self._spider.search_zhidao(keyword+' 百度知道', pn=page).plain,
                display_message=keyword,
                error_file=ZHIDAO_ERROR_FILE,
                error_return=(),
                exception_handle_methods=(
                    [KeyError, lambda:5],
                ),
                retry_time=3,
                sleep_time=self._sleep_time,
            )
            
            for result in res_lst:
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
        if html is None:
            return ([]for _ in range(4))
        title = html.xpath('//*[@id="wgt-ask"]/h1/span//text()')
        best_answer = html.xpath('//div[@class="best-text mb-10 dd"]//text()')
        if not best_answer: best_answer = html.xpath('//div[@class="best-text mb-10"]//text()')
        other_answers = html.xpath('//div[@class="answer-text mb-10"]//text()') 
        if not other_answers: other_answers = html.xpath('//div[@class="answer-text mb-10 line"]//text()')
        links = html.xpath('//*[@id="wgt-related"]/div[1]/ul//a/@href')

        return title, best_answer, other_answers, links
    
    def _crawl_single_url(self, keyword, url):
        if url in self._url_set:
            return
        
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
            
        self._url_set.add(url)
        if self._save_res:
            dump_data(ZHIDAO_ALL_INFO_FILE, crawled_content, mode='a')
            dump_data(ZHIDAO_CRAWLED_URL_FILE, url, 'a')

    def crawl_keywords(self, keyword_list):
        start_log = f"\n{'*'*10}\n{get_cur_time()}\n{'*'*10}"
        log_info(start_log)
        
        log_info('\n=== crawling keywords ===\n')
        todo_keywords = sorted(set(keyword_list)-set(self._key_dic.keys()))
        for keyword in tqdm(todo_keywords, desc='zhidao keywords'):
            urls = self._crawl_urls(keyword)
            if urls:
                self._key_dic[keyword] = sorted(urls)
                if self._save_res:
                    with open(ZHIDAO_CRAWLED_KEYWORD_FILE, 'w', encoding='utf-8') as f:
                        json.dump(self._key_dic, f, indent=4, ensure_ascii=False)
            sleep_random_time(self._sleep_time)
    
    def crawl_urls(self):
        start_log = f"\n{'*'*10}\n{get_cur_time()}\n{'*'*10}"
        log_info(start_log)

        log_info('\n=== crawling urls ===\n')
        todo_urls = {}
        for keyword in self._key_dic:
            for url in self._key_dic[keyword]:
                if url not in self._url_set:
                    todo_urls[url] = keyword
        
        for url, keyword in tqdm(sorted(todo_urls.items()), desc='zhidao urls'):
            exception_handling(
                target_func=lambda:self._crawl_single_url(keyword, url),
                display_message=f'{keyword}\n{url}',
                error_file=ZHIDAO_ERROR_FILE,
                error_return=None,
                exception_handle_methods=(),
                retry_time=self._retry_time,
                sleep_time=self._sleep_time,
            )
                        
       
def main_zhidao_keywords():
    total_keywords = KeywordManager.get_total_keywords()
    zhidao_spider = ZhidaoSpider(
        page_size=2,
        retry_time=3,
        proxy_url=PROXY_URL,
        sleep_time=2.5,
        save_res=True,
    )
    zhidao_spider.crawl_keywords(total_keywords)


def main_zhidao_urls():
    zhidao_spider = ZhidaoSpider(
        page_size=2,
        retry_time=3,
        proxy_url=PROXY_URL,
        sleep_time=2.5,
        save_res=True,
    )
    zhidao_spider.crawl_urls()
    
            
if __name__ == '__main__':
    main_zhidao_keywords()
    main_zhidao_urls()


