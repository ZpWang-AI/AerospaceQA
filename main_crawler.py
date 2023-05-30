import os
import json

from tqdm import tqdm
from pathlib import Path as path

from baike_spider import Baike_spider
from zhidao_spider import Zhidao_spider
from data_utils import load_data, dump_data, load_data_txt
from keyword_extraction import KeywordQueryer, KeywordManager, KeywordFilter


DATASPACE_PATH = './dataspace/'


def main_baike():
    todo_keywords = KeywordManager.get_all_keywords()
    baike_spider = Baike_spider()
    baike_spider.crawl_from_list(todo_keywords)


def main_zhidao():
    todo_keywords = KeywordManager.get_all_keywords()
    zhidao_spider = Zhidao_spider(page_size=2, sleep_time=[1,2,3])
    zhidao_spider.crawl_from_list(todo_keywords)
    

def main_query_new_keywords():
    # keyword_queryer = KeywordQueryer(max_query_len=200, save_keyword=False)
    keyword_queryer = KeywordQueryer()
    
    baike_urls = []
    baike_passage = []
    with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            baike_urls.append(piece['url'])
            baike_passage.append(piece['content'])
    keyword_queryer.get_new_keywords(keys=baike_urls, contents=baike_passage)
    
    zhidao_urls = []
    zhidao_passage = []
    with open('./dataspace/zhidao.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            zhidao_urls.append(piece['url']+'@@1')
            zhidao_passage.append(piece['content1'])
            zhidao_urls.append(piece['url']+'@@2')
            zhidao_passage.append(piece['content2'])
    keyword_queryer.get_new_keywords(keys=zhidao_urls, contents=zhidao_passage)    


def main_filter_new_keywords():
    filter_ = KeywordFilter()
    filter_.filter_keywords()
    
if __name__ == "__main__":
    for i in range(1):
        # main_baike()    
        # main_zhidao()
        # main_query_new_keywords()
        # main_filter_new_keywords()
    
        KeywordManager.get_new_filter_keywords()
        
