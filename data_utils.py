import os
import random
import json
import csv 
import logging
import pandas as pd

from collections import OrderedDict, defaultdict
from functools import reduce
from pathlib import Path as path
from typing import *

# try:
#     from docx import Document
# except:
#     print('warning: pandas or python-docx has not been installed.')


def load_data(file_path, default=None, merge_jsonl=False):
    file_path = path(file_path)
    if not file_path.exists():
        if default is None:
            print(f'== {file_path} not exists ==')
            return 
        else:
            return default
    if file_path.suffix == '.txt':
        with open(file_path, 'r', encoding='utf-8')as f:
            lines = list(filter(lambda x:x, map(lambda x:x.strip(), f.readlines())))
        return lines    
    elif file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8')as f:
            dic = json.load(f)
        return dic
    elif file_path.suffix == '.jsonl':
        with open(file_path, 'r', encoding='utf-8')as f:
            lines = list(filter(lambda x:x, map(lambda x:x.strip(), f.readlines())))
            dics = list(map(json.loads, lines))
        if merge_jsonl:
            kv = []
            for dic in dics:
                kv.extend(dic.items())
            return dict(kv)
        else:
            return dics
    else:
        print(f'== {file_path} has wrong suffix ==')
        return 


def dump_data(file_path, content, mode='a+', indent=None):
    file_path = path(file_path)
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8')as f:
            f.write('')
    if file_path.suffix == '.txt':
        with open(file_path, mode=mode, encoding='utf-8')as f:
            f.write(content+'\n')
    elif file_path.suffix == '.json':
        with open(file_path, mode=mode, encoding='utf-8')as f:
            json.dump(content, f, ensure_ascii=False, indent=indent)
    elif file_path.suffix == '.jsonl':
        with open(file_path, mode=mode, encoding='utf-8')as f:
            f.write(json.dumps(content, ensure_ascii=False)+'\n')
    else:
        print(f'== {file_path} has wrong suffix ==')
        return 


def json2jsonl(source_json, target_jsonl):
    content = load_data(source_json, default={})
    content: dict
    if path(target_jsonl).exists():
        status = input(f'target file {target_jsonl} exists\ncontinue 0 or 1')
        if status != '1':
            return
    with open(target_jsonl, 'w', encoding='utf-8')as f:
        for k, v in content.items():
            f.write(json.dumps({k:v}, ensure_ascii=False)+'\n')
    print(f'from {source_json} to {target_jsonl}')



if __name__ == '__main__':
    # print(load_data('./dataspace/todo_keywords.txt'))
    
    # from settings import (KEYWORD_QUERY_FILE_JSON,
    #                       KEYWORD_QUERY_FILE_JSONL,
    #                       KEYWORD_FILTER_FILE_JSON,
    #                       KEYWORD_FILTER_FILE_JSONL,
    #                       ZHIDAO_CRAWLED_KEYWORD_FILE_JSON,
    #                       ZHIDAO_CRAWLED_KEYWORD_FILE_JSONL,
    #                       )
    # json2jsonl(KEYWORD_QUERY_FILE_JSON, KEYWORD_QUERY_FILE_JSONL)
    # json2jsonl(KEYWORD_FILTER_FILE_JSON, KEYWORD_FILTER_FILE_JSONL)
    # json2jsonl(ZHIDAO_CRAWLED_KEYWORD_FILE_JSON, ZHIDAO_CRAWLED_KEYWORD_FILE_JSONL)
    
    # print(load_data('./dataspace/keyword.query.jsonl', {}, merge_jsonl=True))
    
    pass