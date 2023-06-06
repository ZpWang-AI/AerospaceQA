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
from settings import (ZHIDAO_ALL_INFO_FILE_JSONL,
                      ZHIDAO_CRAWLED_KEYWORD_FILE_JSON,
                      ZHIDAO_LOG_FILE_TXT,
                      ZHIDAO_ERROR_FILE_TXT,
                      PROXY_URL,
                      )

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
# headers = None

fail_crawl_urls = 'no urls'
fail_log_prefix = '@fail@ '


def log_info(*args, sep=' '):
    info = sep.join(args)
    print(info)
    dump_data(ZHIDAO_LOG_FILE_TXT, info, mode='a')
            

class ZhidaoSpider:
    def __init__(self, 
                 page_size=2, 
                 retry_time=3, 
                 proxy_url=None, 
                 sleep_time=2.5, 
                 save_res=True,
                 decode_mode='utf-8'
                 ):
        self._page_size = page_size
        self._retry_time = retry_time
        self._proxy_url = proxy_url
        self._sleep_time = sleep_time
        self._save_res = save_res
        self._decode_mode = decode_mode  # 'gb2312', 'utf-8'

        self._spider = BaiduSpider()
        self._normalizer = Normalizer()
        
        self._record = load_data(ZHIDAO_CRAWLED_KEYWORD_FILE_JSON, default={})
        
    def _log(self, keyword, url, info):
        if keyword not in self._record:
            self._record[keyword] = {}
        self._record[keyword][url] = info if type(info) == bool else str(info)
        if self._save_res:
            dump_data(ZHIDAO_CRAWLED_KEYWORD_FILE_JSON, self._record, 'w', indent=4)
    
    def _del_log(self, keyword, url):
        if keyword in self._record and url in self._record[keyword]:
            del self._record[keyword][url]  
        
    def _decode_ans(self, answer):
        answer = answer.encode('iso-8859-1', errors='ignore')
        answer = answer.decode(self._decode_mode, errors='ignore')
        return answer
            
    def _crawl_urls(self, keyword):
        urls = set()
        
        def exception_handle_func(err):
            self._log(keyword, fail_crawl_urls, f'{type(err)}\n{str(err)}')
            if type(err) == KeyError:
                return 5
            if type(err) == requests.exceptions.SSLError and 'Max retries exceeded with url' in str(err):
                return 5
        
        for page in range(1, self._page_size+1):
            res_lst = exception_handling(
                target_func=lambda:self._spider.search_zhidao(keyword+' 百度知道', pn=page).plain,
                display_message=keyword,
                error_file=ZHIDAO_ERROR_FILE_TXT,
                error_return=(),
                exception_handle_func=exception_handle_func,
                retry_time=3,
                sleep_time=self._sleep_time,
            )
            for result in res_lst:
                urls.add(result['url'])
        if urls:
            self._del_log(keyword, fail_crawl_urls)
        return sorted(urls)

    def _crawl_answers(self, keyword, url):
        response = requests.get(
            url, 
            headers=headers, 
            proxies=get_proxy(proxy_url=self._proxy_url, return_str=False)
        )
        if response is None:
            self._log(keyword, url, fail_log_prefix+'no response')
            return ([]for _ in range(4))
            
        # response.encoding = 'gb1213'
        html = etree.HTML(response.text)
        if html is None:
            self._log(keyword, url, fail_log_prefix+'no html')
            return ([]for _ in range(4))
        
        title = html.xpath('//*[@id="wgt-ask"]/h1/span//text()')
        best_answer = html.xpath('//div[@class="best-text mb-10 dd"]//text()')
        if not best_answer: best_answer = html.xpath('//div[@class="best-text mb-10"]//text()')
        other_answers = html.xpath('//div[@class="answer-text mb-10"]//text()') 
        if not other_answers: other_answers = html.xpath('//div[@class="answer-text mb-10 line"]//text()')
        links = html.xpath('//*[@id="wgt-related"]/div[1]/ul//a/@href')
        
        if not best_answer and not other_answers:
            self._log(keyword, url, fail_log_prefix+'no answer')
            return ([]for _ in range(4))    

        return title, best_answer, other_answers, links
    
    def _crawl_single_url(self, keyword, url):
        title, best_answer, other_answers, links = self._crawl_answers(keyword, url)
        if not best_answer and not other_answers:
            return
        
        links = [url+link for link in links]
        title, best_answer, other_answers, links = map(
            lambda x: self._normalizer.cleaner(self._decode_ans(''.join(x).strip())),
            [title, best_answer, other_answers, links],
        )
            
        crawled_content = {
            'keyword':keyword, 
            'url':url, 
            'title':title, 
            'content1':best_answer,
            'content2':other_answers, 
            'related_links':links, 
            'last_time':time.asctime(),
        }
            
        if self._save_res:
            dump_data(ZHIDAO_ALL_INFO_FILE_JSONL, crawled_content, mode='a')
        return True

    def crawl_keywords(self, keyword_list):
        start_log = f"\n{'*'*10}\n{get_cur_time()}\n{'*'*10}"
        log_info(start_log)
        
        keyword_list = set(keyword_list)
        keyword_list = filter(
            lambda x:x not in self._record or any(v is not True for v in self._record[x].values()),
            keyword_list,
        )
        keyword_list = sorted(keyword_list)
        
        fail_keyword_cnt = 0
        for keyword in tqdm(keyword_list, desc='zhidao'):
            if keyword not in self._record or fail_crawl_urls in self._record[keyword]:
                urls = self._crawl_urls(keyword)
                for url in urls:
                    self._log(keyword, url, False)
            else:
                cur_record = self._record[keyword]
                urls = list(filter(lambda x:cur_record[x] is not True, cur_record.keys()))
            if not urls:
                continue
            
            success_cnt = 0
            for url in tqdm(urls, desc=keyword):
                def exception_handle_func(err):
                    self._log(keyword, url, fail_log_prefix+f'no {type(err)}\n{str(err)}')
                    if type(err) == requests.exceptions.SSLError and 'Max retries exceeded with url' in str(err):
                        return 5
                    if type(err) == requests.exceptions.ProxyError and 'Max retries exceeded with url' in str(err):
                        return 5
                    if "Invalid URL 'no urls'" in str(err):
                        return 5
                                   
                crawl_res = exception_handling(
                    target_func=lambda:self._crawl_single_url(keyword, url),
                    display_message=f'{keyword}\n{url}',
                    error_file=ZHIDAO_ERROR_FILE_TXT,
                    error_return=None,
                    exception_handle_func=exception_handle_func,
                    retry_time=self._retry_time,
                    sleep_time=self._sleep_time,
                )
                
                if crawl_res:
                    self._log(keyword, url, True)
                    success_cnt += 1
                sleep_random_time(self._sleep_time)
            
            if success_cnt:
                log_info(f'\n{keyword} success, {success_cnt} crawled\n')
            else:
                fail_keyword_cnt += 1
                if fail_keyword_cnt >= 3:
                    print('\n too many failure, no more crawling')
                    return
            sleep_random_time(self._sleep_time)
          
       
def main_zhidao():
    total_keywords = KeywordManager.get_final_keywords()
    zhidao_spider = ZhidaoSpider(
        page_size=2,
        retry_time=3,
        proxy_url=PROXY_URL,
        sleep_time=2.5,
        save_res=True,
    )
    zhidao_spider.crawl_keywords(total_keywords)
    
            
if __name__ == '__main__':
    main_zhidao()


