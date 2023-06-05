import os
import random
import json
import csv 
import logging
import pandas as pd

from collections import OrderedDict, defaultdict
from pathlib import Path as path
from typing import *

# try:
#     from docx import Document
# except:
#     print('warning: pandas or python-docx has not been installed.')


def load_data(file_path, default=None):
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







if __name__ == '__main__':
    print(load_data('./dataspace/todo_keywords.txt'))