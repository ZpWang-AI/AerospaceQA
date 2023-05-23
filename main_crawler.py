import os
import json

from tqdm import tqdm
from pathlib import Path as path

from baike_spider import Baike_spider
from zhidao_spider import Zhidao_spider
from data_utils import load_data, dump_data, load_data_txt
from keyword_extraction import KeywordQueryer


DATASPACE_PATH = './dataspace/'


def main(round_num, sleep_time, crawl_baike=True, crawl_zhidao=True):
    # load keywords, init & todo
    init_path = path(DATASPACE_PATH, 'init_keywords.txt')
    todo_path = path(DATASPACE_PATH, 'todo_keywords.txt')
    init_path.parent.mkdir(parents=True, exist_ok=True)
    todo_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.touch(exist_ok=True)
    todo_path.touch(exist_ok=True)

    todo_keywords = load_data_txt(init_path)+load_data_txt(todo_path)
    todo_keywords = list(set(todo_keywords))
    used_keywords = set()
    
    # load crawled_keywords
    baike_spider = Baike_spider()
    zhidao_spider = Zhidao_spider()
    keyword_queryer = KeywordQueryer()
    
    for r in range(1, round_num+1):
        print(f'\n{"="*10} round {r} {"="*10}\n')
        
        if crawl_baike:
            baike_spider.crawl_from_list(todo_keywords)
            new_baike_passage = []
            with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
                for line in f.readlines():
                    piece = json.loads(line)
                    if piece['keyword'] in todo_keywords:
                        new_baike_passage.append(piece['content'])
        else:
            new_baike_passage = []

        if crawl_zhidao:
            zhidao_new_data = zhidao_spider.crawl_from_list(todo_keywords)
            new_zhidao_passage1 = [item['content1'] for item in zhidao_new_data if item]
            new_zhidao_passage2 = [item['content2'] for item in zhidao_new_data if item]
        else:
            new_zhidao_passage1 = []
            new_zhidao_passage2 = []

        # update keywords from openai
        baike_todo_keywords = keyword_queryer.get_new_keywords(new_baike_passage)
        zhidao_todo_keywords1 = keyword_queryer.get_new_keywords(new_zhidao_passage1)
        zhidao_todo_keywords2 = keyword_queryer.get_new_keywords(new_zhidao_passage2)
        todo_keywords = baike_todo_keywords + zhidao_todo_keywords1 + zhidao_todo_keywords2
        todo_keywords = list(set(todo_keywords))
        
        print(todo_keywords)
        dump_data(todo_keywords, todo_path, 'plain')
        

if __name__ == "__main__":
    # print(get_new_keywords(['你看这个航天飞机，他又大又硬']))
    round_num = 4
    sleep_time = 3
    main(round_num, sleep_time, crawl_baike=True, crawl_zhidao=False)
