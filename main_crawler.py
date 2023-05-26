import os
import json

from tqdm import tqdm
from pathlib import Path as path

from baike_spider import Baike_spider
from zhidao_spider import Zhidao_spider
from data_utils import load_data, dump_data, load_data_txt
from keyword_extraction import KeywordQueryer, KeywordManager


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
    
    baike_passage = []
    with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            baike_passage.append(piece['content'])
    keyword_queryer.get_new_keywords(baike_passage)
    
    zhidao_passage = []
    with open('./dataspace/zhidao.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            zhidao_passage.append(piece['content'])
    keyword_queryer.get_new_keywords(zhidao_passage)    
    
    KeywordManager.get_new_keywords()

    
if __name__ == "__main__":
    for i in range(1):
        # main_baike()    
        # main_zhidao()
        main_query_new_keywords()
