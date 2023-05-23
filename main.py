# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023/05/17 14:19:55
@Author  :   Zhifeng Li
@Contact :   li_zaaachary@outlook.com
@Desc    :   

Recorded list:
- init_keywords
- todo_keywords

- baike_crawled_keywords
- baike_error_keywords
- baike_passages

- zhidao_crawled_urls       # input & output
- zhidao_crawled_keywords
- zhidao_error_keywrods     # 此前失败 -> 没有，网络
- zhidao_passages

- log
'''
import os
join = os.path.join

from tqdm import tqdm

from baike_spider import Baike_spider
from zhidao_spider import Zhidao_spider
from data_utils import load_data, dump_data
from keyword_extraction import get_response


def get_new_keywords(passages):
    MAX_LEN = 1000
    new_keywords = []
    print('openai processing')
    for passage in tqdm(passages):
        if not passage.strip():
            continue
        keywords = get_response(passage[:MAX_LEN])
        new_keywords.extend(keywords)
    return list(set(new_keywords))

def main(round_num, dataspace_path, sleep_time):

    # load keywords, init & todo
    todo_keywords = list()

    init_path = join(dataspace_path, 'init_keywords.txt')
    todo_path = join(dataspace_path, 'todo_keywords.txt')
    if os.path.exists(init_path):
        todo_keywords.extend(load_data(init_path, 'plain'))
    if os.path.exists(todo_path):
        todo_keywords.extend(load_data(todo_path, 'plain'))

    # load crawled_keywords
    baike_spider = Baike_spider()
    zhidao_spider = Zhidao_spider()
    for rn in range(round_num):
        print(f'turn {rn}')
        # crawl from baike
        baike_new_data, error_keywords, crawled_keywords = baike_spider.crawl_from_list(todo_keywords)
        new_baike_passage = [item['content'] for item in baike_new_data if item]

        # crawl from zhidao
        # update zhidao list
        zhidao_new_data = zhidao_spider.crawl_from_list(keyword_list=todo_keywords)
        new_zhidao_passage1 = [item['content1'] for item in zhidao_new_data if item]
        new_zhidao_passage2 = [item['content2'] for item in zhidao_new_data if item]

        # update keywords from openai
        baike_todo_keywords = get_new_keywords(new_baike_passage)
        zhidao_todo_keywords1 = get_new_keywords(new_zhidao_passage1)
        zhidao_todo_keywords2 = get_new_keywords(new_zhidao_passage2)
        todo_keywords = baike_todo_keywords + zhidao_todo_keywords1 + zhidao_todo_keywords2

        print(todo_keywords)
        dump_data(todo_keywords, join(dataspace_path, 'todo_keywords.txt'), 'plain')
        

if __name__ == "__main__":
    round_num = 4
    sleep_time = 3
    dataspace_path = "./dataspace/"
    main(round_num, dataspace_path, sleep_time)
