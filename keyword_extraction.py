# -*- coding: utf-8 -*-
import openai
import datetime
import time
import traceback
import json
import os
import pandas as pd

from pathlib import Path as path
from tqdm import tqdm
from collections import OrderedDict

from data_utils import load_data, dump_data
from openai_api import get_response_chatcompletion
from openai_apikey import api_key
from data_manager import DataManager
from settings import (KEYWORD_FOLD,
                      KEYWORD_QUERY_FILE_JSON,
                      KEYWORD_FILTER_FILE_JSON)

openai.api_key = api_key

sentence_sep = '。？！.?!．'
# keyword_query_prompt = '''请从文章中抽取出所有的航空航天领域科学技术术语，以列表形式给出。
# 输出格式：
# - xxx
# - xxx
# 文章：
# '''.strip()
keyword_query_prompt = '''
请从文章中抽取出所有的航空航天领域的科学技术术语，以列表形式给出。
输出格式：
- xxx
- xxx
样例：
- 涡轮喷气式发动机
- 超低空飞行
- 神舟十二号载人飞船
- 近地卫星导航系统
文章：
'''.strip()
# keyword_filter_prompt = '''请判断下列词语是否与航天航空领域存在直接或潜在的关系。输出两行，以逗号分割。
# 输出格式
# 是: xxx,xxx,xxx
# 否: xxx,xxx,xxx
# '''.strip()
# keyword_filter_prompt = '''请判断下列词语是否与航天航空领域存在直接关系。输出两行，以逗号分割。
# 输出格式
# 是: xxx,xxx,xxx
# 否: xxx,xxx,xxx
# '''.strip()
keyword_filter_prompt = '''请判断下列词语是否属于航天航空领域。输出两行，以逗号分割。
输出格式：
是: xxx,xxx,xxx
否: xxx,xxx,xxx
词语：
'''.strip()


class KeywordQueryer:
    def __init__(self, 
                 prompt,
                 engine='gpt-3.5-turbo',
                 max_query_len=1000, 
                 max_ans_token=2048, 
                 retry_time=3,
                 save_keyword=True,
                 ) -> None:
        print(f'prompt\n{prompt}')
        self._prompt = prompt
        self._engine = engine
        self._max_query_len = max_query_len
        self._max_ans_token = max_ans_token
        self._retry_time = retry_time
        self._save_keyword = save_keyword
    
    def _get_response(self, content):
        message_list = [
            {'role': 'user', 'content': f'{self._prompt}\n{content}'},
        ]
        
        output_keyword = get_response_chatcompletion(
            messages=message_list,
            engine=self._engine,
            max_tokens=self._max_ans_token,
            retry_time=self._retry_time,
        )
        output_keyword = output_keyword.split('\n')
        output_keyword = filter(lambda x:len(x)>2 and x[0]=='-', output_keyword)
        output_keyword = map(lambda x:x[1:].strip(), output_keyword)
        return list(output_keyword)

    def _clip_content(self, content):
        def clip_sentence(sentence):
            return [sentence[p:p+self._max_query_len] 
                    for p in range(0, len(sentence), self._max_query_len)]
                
        sentences = []
        cur_sentence = ''
        for d in content:
            cur_sentence += d
            if d in sentence_sep:
                sentences.extend(clip_sentence(cur_sentence))
                cur_sentence = ''
        if cur_sentence:
            sentences.extend(clip_sentence(cur_sentence))
            
        cur_content = ''
        for sen in sentences:
            if len(cur_content+sen) > self._max_query_len:
                yield cur_content
                cur_content = sen
            else:
                cur_content += sen
        yield cur_content
    
    def get_new_keywords(self, keys, contents):
        record = load_data(KEYWORD_QUERY_FILE_JSON, default={})
    
        todo_lst = []
        for key, content in zip(keys, contents):
            content = content.strip()
            if content and key not in record:
                todo_lst.append([key, content])
        todo_lst.sort()
            
        print('\n=== openai processing ===\n')
        for key, content in tqdm(todo_lst, desc='query keywords'):
            new_keywords = []
            for cliped_content in self._clip_content(content):
                cur_keywords = self._get_response(cliped_content)
                new_keywords.extend(cur_keywords)
            
            record[key] = new_keywords
            if self._save_keyword:
                dump_data(KEYWORD_QUERY_FILE_JSON, record, 'w', indent=4)


class KeywordFilter:
    def __init__(self,
                 prompt,
                 engine='gpt-3.5-turbo',
                 max_filter_cnt=100, 
                 max_query_len=None,
                 max_ans_token=2048, 
                 retry_time=3,
                 save_keyword=True,
                 ) -> None:    
        print(f'prompt\n{prompt}')
        self._prompt = prompt
        self._engine = engine
        self._max_filter_cnt = max_filter_cnt
        self._max_ans_token = max_ans_token
        self._retry_time = retry_time
        self._save_keyword = save_keyword
        
        self._max_query_len = max_query_len if max_query_len else 1000
    
    def _get_response(self, content):
        message_list = [
            {'role': 'user', 'content': f'{self._prompt}\n{content}'},
        ]
        
        output_filter = get_response_chatcompletion(
            messages=message_list,
            engine=self._engine,
            max_tokens=self._max_ans_token,
            retry_time=self._retry_time,
        )
        output_filter = output_filter.split('\n')
        output_res = {}
        
        def split_line(line):
            words = line[2:].split(',')
            words = map(lambda x:x.strip(), words)
            words = filter(lambda x:x, words)
            return list(words)
        
        for line in output_filter:
            line = line.strip()
            if not line:
                continue
            if line[0] == '是':
                output_yes = split_line(line)
                for w in output_yes:
                    output_res[w] = True
            if line[0] == '否':
                output_no = split_line(line)
                for w in output_no:
                    output_res[w] = False
        return output_res

    def _clip_content(self, keywords):
        content = '\n'.join(keywords)
        if len(content) <= self._max_query_len:
            yield content
            return
        cur_content = ''
        for k in keywords:
            if len(cur_content+'\n'+k) > self._max_query_len:
                yield cur_content
                cur_content = k
            else:
                cur_content += '\n'+k
        yield cur_content
        
    def filter_keywords(self, todo_keywords, deduplicate=False):
        record_filter = load_data(KEYWORD_FILTER_FILE_JSON, default={})
        if deduplicate:
            todo_keywords = sorted(set(todo_keywords))

        print('\n=== openai processing ===\n')
        for p in tqdm(list(range(0, len(todo_keywords), self._max_filter_cnt)), desc='filter keywords'):
            cur_keywords = todo_keywords[p:p+self._max_filter_cnt]
            for content in self._clip_content(cur_keywords):
                filter_res = self._get_response(content)
                record_filter.update(filter_res)
                if self._save_keyword:
                    dump_data(KEYWORD_FILTER_FILE_JSON, record_filter, 'w', indent=4)  


class KeywordManager:
    
    @staticmethod
    def keyword_excel2txt():
        for file in os.listdir(KEYWORD_FOLD):
            file = KEYWORD_FOLD/file
            if file.suffix not in ['.xls', '.xlsx']:
                continue
            file_excel = file
            file_txt = file.with_suffix('.txt')
            if file_txt.exists():
                continue
            
            keyword_yes = []
            for sym in ['是', '1', 1]:
                df_keyword = pd.read_excel(file_excel)
                df_keyword = df_keyword.loc[df_keyword.iloc[:, 1]==sym]
                df_keyword = df_keyword.iloc[:, 0]
                keyword_yes.extend(df_keyword.tolist())
            str_keyword = '\n'.join(map(str, keyword_yes))
            dump_data(file_txt, str_keyword, 'w')
            print(f'keyword from {file_excel} to {file_txt}')
    
    @staticmethod
    def get_final_keywords():
        return DataManager.keyword_final()
            

def main_query_new_keywords():
    queried_keywords = load_data(KEYWORD_QUERY_FILE_JSON, default={})
    keyword_queryer = KeywordQueryer(
        prompt=keyword_query_prompt,
    )
    
    baike_urls = []
    baike_passage = []
    with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            if piece['url'] not in queried_keywords:
                baike_urls.append(piece['url'])
                baike_passage.append(piece['content'])
    keyword_queryer.get_new_keywords(keys=baike_urls, contents=baike_passage)
    
    zhidao_urls = []
    zhidao_passage = []
    with open('./dataspace/zhidao.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        for line in f.readlines():
            piece = json.loads(line)
            if piece['url']+'@@1' not in queried_keywords:
                zhidao_urls.append(piece['url']+'@@1')
                zhidao_passage.append(piece['content1'])
            if piece['url']+'@@2' not in queried_keywords:
                zhidao_urls.append(piece['url']+'@@2')
                zhidao_passage.append(piece['content2'])
    keyword_queryer.get_new_keywords(keys=zhidao_urls, contents=zhidao_passage)    


def main_filter_new_keywords():
    filter_todo = DataManager.keyword_filter_k_todo()
    filter_ = KeywordFilter(
        prompt=keyword_filter_prompt,
    )
    filter_.filter_keywords(filter_todo)
    
    
def main_excel2txt_manual_todo(part_size=(), sheet_names=()):
    KeywordManager.keyword_excel2txt()
    print('excel to txt done\n')
    
    if not part_size:
        print('no split')
        return
    if not sheet_names:
        sheet_names = range(1, len(part_size)+1)
    assert len(part_size) == len(sheet_names)
    
    manual_todo = DataManager.keyword_manual_k_todo()[:sum(part_size)]
    excel_file = path(f'./dataspace/data_keyword_{str(datetime.date.today())}.xlsx')
    if excel_file.exists():
        os.remove(excel_file)
    
    needle = 0
    for p, (size, sheet_name) in enumerate(zip(part_size, sheet_names)):
        df = pd.DataFrame(manual_todo[needle:needle+size])
        needle += size
        with pd.ExcelWriter(excel_file, mode=('a' if p else 'w'))as f:
            df.to_excel(f, sheet_name=str(sheet_name), index=False, header=False)
    print(f'{len(manual_todo)} manual todo keywords prepared')
    
    
if __name__ == '__main__':
    main_excel2txt_manual_todo([2000]*3)
    # sentence = '''看我的收藏0有用+1已投票0轨道器播报编辑锁定讨论上传视频特型编辑太空拖船轨道器是指往来于航天站与空间基地之间的载人或无人飞船。它的主要用途是更换、修理航天站上的仪器设备。补给消耗品，从航天站取回资料和空间加工的产品等。由于它专门来往于各个空间站，又被称为“太空拖船”。中文名轨道器别名太空拖船往返航天站与空间基地用途更换、修理航天站上的仪器设备相关视频查看全部轨道飞行器分为两种。一种是活动范围较小的，叫做轨道机动飞行器；另一种是在大范围内实行轨道转移的，成为轨道转移飞行器。可以搭载七名宇航员在太空至少逗留10天。机舱内有三层甲板：飞行甲板、中甲板和设有生命支持系统的底层甲板。轨道飞行器长37.24米，高17.27米，翼展29.79米，载荷舱尺寸18.3*4.6米，轨道速度每小时28800公里，可容忍温度1500摄氏度，轨道高度185公里至1000公里，持续时间10至16天。词条图册更多图册'''
    # kq = KeywordQueryer(save_keyword=False)
    # print(kq.get_new_keywords(['123'], [sentence]))
    
    # kf = KeywordFilter(save_keyword=False)
    # kf.filter_keywords
    
    # KeywordManager.keyword_excel2txt()
    
    # all_keywords = KeywordManager.get_all_keywords()
    # print(len(all_keywords))
    
    pass