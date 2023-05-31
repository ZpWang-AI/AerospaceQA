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
                      ZHIDAO_ERROR_FILE,)

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
        self._sleep_time = sleep_time

        self._normalizer = Normalizer()

        self._not_found = set()
        self._keyDCT = OrderedDict()
        self.urlDCT = OrderedDict()
        self.content = []

        if os.path.exists(crawled_file):
            # print('Load crawled keywords...')
            with open(crawled_file,'r',encoding='utf-8') as f:
                self._keyDCT = json.load(f)
                for key, urls in self._keyDCT.items():
                    for url in urls:
                        self.urlDCT[url] = key

        if os.path.exists(not_found_word_file):
            # print('Load not found keywords...')
            with open(not_found_word_file,'r',encoding='utf-8') as f:
                lines = f.readlines()
            self._not_found = set(map(lambda x: x.strip(), lines))

    def crawl_urls(self, key):
        urls = set()
        print("{} Crawl URLS...".format(key))
        for page in range(1, self._page_size+1):
            try:
                reslst = spider.search_zhidao(key+' 百度知道', pn=page).plain
            except:
                print('-'*20)
                print(key)
                print('-'*20)
                print(traceback.format_exc())
                print('-'*20)
                continue
            
            if not len(reslst): continue
            for result in reslst:
                url = result['url']
                if url in self.urlDCT:
                    continue
                urls.add(result['url'])
        return urls

    def crawl_answers(self, url):
        retry_cnt = 0
        while 1:
            retry_cnt += 1
            try:
                pass
            except BaseException as err:
                if retry_cnt == 1:
                    print('=='*10)
                    # print(messages)
                    print('-'*10)
                print(traceback.format_exc())
                print(f'>> retry {retry_cnt} <<')
                print(f'>> error {str(err)} <<')
                print('-'*10)
                if retry_cnt == retry_time:
                    # return ''
                    pass
                else:
                    time.sleep(wait_seconds)
        response = requests.get(url, headers=headers, proxies=get_proxy(return_str=False))
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
    
    def crawl_from_list(self, keyword_list):
        total_data = self.crawl_all(keyword_list=keyword_list)
        return total_data
    
    def crawl_all(self, keyword_file=None, keyword_list=[]):
        
        if keyword_list:
            keys = keyword_list
        elif keyword_file:
            with open(keyword_file, 'r', encoding='utf-8') as f:
                keys = set(map(lambda x: x.strip(), f.readlines()))
        else: return []

        new_contents = []

    
        for key in tqdm(keys):
            print("{} Crawl KEYS...".format(key))
            if key in self._keyDCT:
                print("{} zhidao has been crawled already.".format(key))
                continue

            is_err = True

            urls = self.crawl_urls(key)

            for url in tqdm(urls):
                # print("{} {} Crawl CONTENTS...".format(key, url))
                title, best_answer, other_answers, links = self.crawl_answers(url)
                links = [url+link for link in links]
                if not (best_answer or other_answers):
                    # print("{} {} Crawl CONTENTS Failed!".format(key, url))
                    continue
                # print("{} {} Crawl CONTENTS Success!".format(key, url))

                is_err = False
                
                title = self._normalizer.cleaner(''.join(title).strip())
                best_answer = self._normalizer.cleaner(''.join(best_answer).strip())
                other_answers = self._normalizer.cleaner(''.join(other_answers).strip())
                    
                crawled_content = {'keyword':key, 'url':url, 'title':title, \
                                    'content1':best_answer,'content2':other_answers, \
                                    'related_links':links, 'last_time':time.asctime()}
                
                self.content.append(crawled_content)   
                new_contents.append(crawled_content)   
                self._keyDCT.setdefault(key, []).append(url)
                self.urlDCT.setdefault(url, key)

                # print("{} {} Write CONTENTS...".format(key, url))
                with open(all_info_file,'a+', encoding='utf-8') as o:
                    json.dump(crawled_content, o, ensure_ascii=False)
                    o.write('\n') 
                # print("{} {} Write Crawled...".format(key, url))
                with open(crawled_file, 'w', encoding='utf-8') as f:
                    json.dump(self._keyDCT, f, indent=4, ensure_ascii=False)

            if is_err: 
                self._not_found.add(key)
                # print("Write Not Found...")
                with open(not_found_word_file, 'w', encoding='utf-8') as f:
                    for key in tqdm(self._not_found):
                        f.write(key+ '\n')

            sleep_random_time(self._sleep_time)

        return new_contents
            
if __name__ == '__main__':
    zhidao_spider = Zhidao_spider() 
    zhidao_spider.crawl_all(r'keyword_file/4_27_12_01.txt')


