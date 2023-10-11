import os
import json

from collections import defaultdict
from pathlib import Path as path

from data_utils import load_data, dump_data
from settings import (BAIKE_ALL_INFO_FILE_JSONL,
                      ZHIDAO_ALL_INFO_FILE_JSONL,
                      KEYWORD_QUERY_FILE_JSONL)
from data_manager import DataManager, KeywordProcesser


def main_passage2keywords():
    total = []
    total_passage = {}

    baike_passage = load_data(BAIKE_ALL_INFO_FILE_JSONL, [])
    for line in baike_passage:
        total_passage[line['url']] = line['content'] 
    zhidao_passage = load_data(ZHIDAO_ALL_INFO_FILE_JSONL, [])
    for line in zhidao_passage:
        con1 = line['content1'].strip()
        con2 = line['content2'].strip()
        if con1:
            total_passage[line['url']+'@@1'] = con1
        if con2:
            total_passage[line['url']+'@@2'] = con2
    
    total_manual = DataManager.keyword_manual_k_yes(return_set=True)

    query_data = load_data(KEYWORD_QUERY_FILE_JSONL, {}, merge_jsonl=True)
    for k in sorted(query_data):
        if k not in total_passage:
            print(k)
            return
        keywords = KeywordProcesser.process_func(query_data[k])
        keywords = list(filter(lambda x:x in total_manual, keywords))
        total.append({'passage':total_passage[k], 'keywords':keywords})
    
    save_file = path('./dataspace/passage2keywords.jsonl')

    if save_file.exists():
        os.remove(save_file)
    for p in total:
        dump_data(save_file, p, mode='a+')
    


if __name__ == '__main__':
    main_passage2keywords()