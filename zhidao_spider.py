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

from proxy_utils import get_proxy
spider = BaiduSpider()
page_size = 3
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

not_found_word_file = 'dataspace/zhidao.Not_found_keyword_list.txt'
crawled_file = 'dataspace/zhidao.crawled_keyword.json'
all_info_file = 'dataspace/zhidao.all_crawled_info.jsonl'


def decorator_crawl_answer(func):
    def new_func(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except BaseException as err:
            print('-'*10)
            print(err)
            print('-'*10)
            print(traceback.format_exc())
            return ([]for _ in range(4))
    return new_func


class Zhidao_spider:
    def __init__(self, page_size=3, sleep_time=[1,2,3]):
        self.page_size = page_size
        self.sleep_time = sleep_time

        self.normalizer = zhidao_norm.normalizer() 

        self.NotFoundSet = set()
        self.keyDCT = OrderedDict()
        self.urlDCT = OrderedDict()
        self.content = []

        if os.path.exists(crawled_file):
            # print('Load crawled keywords...')
            with open(crawled_file,'r',encoding='utf-8') as f:
                self.keyDCT = json.load(f)
                for key, urls in self.keyDCT.items():
                    for url in urls:
                        self.urlDCT[url] = key

        if os.path.exists(not_found_word_file):
            # print('Load not found keywords...')
            with open(not_found_word_file,'r',encoding='utf-8') as f:
                lines = f.readlines()
            self.NotFoundSet = set(map(lambda x: x.strip(), lines))


    def crawl_urls(self, key):
        urls = set()
        print("{} Crawl URLS...".format(key))
        for page in range(1, self.page_size+1):
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


    @decorator_crawl_answer
    def crawl_answers(self, url):
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
            if key in self.keyDCT:
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
                
                title = self.normalizer.cleaner(''.join(title).strip())
                best_answer = self.normalizer.cleaner(''.join(best_answer).strip())
                other_answers = self.normalizer.cleaner(''.join(other_answers).strip())
                    
                crawled_content = {'keyword':key, 'url':url, 'title':title, \
                                    'content1':best_answer,'content2':other_answers, \
                                    'related_links':links, 'last_time':time.asctime()}
                
                self.content.append(crawled_content)   
                new_contents.append(crawled_content)   
                self.keyDCT.setdefault(key, []).append(url)
                self.urlDCT.setdefault(url, key)

                # print("{} {} Write CONTENTS...".format(key, url))
                with open(all_info_file,'a+', encoding='utf-8') as o:
                    json.dump(crawled_content, o, ensure_ascii=False)
                    o.write('\n') 
                # print("{} {} Write Crawled...".format(key, url))
                with open(crawled_file, 'w', encoding='utf-8') as f:
                    json.dump(self.keyDCT, f, indent=4, ensure_ascii=False)

            if is_err: 
                self.NotFoundSet.add(key)
                # print("Write Not Found...")
                with open(not_found_word_file, 'w', encoding='utf-8') as f:
                    for key in tqdm(self.NotFoundSet):
                        f.write(key+ '\n')

            time.sleep(random.choice(self.sleep_time))

        return new_contents
            
if __name__ == '__main__':
    zhidao_spider = Zhidao_spider() 
    zhidao_spider.crawl_all(r'keyword_file/4_27_12_01.txt')


