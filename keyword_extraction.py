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

from data_utils import load_data_txt

# openai.api_key = "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"
openai.api_key = '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'
# openai.proxy = "http://127.0.0.1:1087"
openai.proxy = '7890'


DATA_FOLD = path('./dataspace/')
KEYWORD_FOLD = path('./dataspace/keywords/')
RECORD_FILE_KEYWORD = path('./dataspace/queried_keywords.json')


class KeywordQueryer:
    def __init__(self, 
                 prompt="请从文章中抽取出所有的航空航天领域科学技术术语，以列表形式给出。\n输出格式\n- xxx\n- xxx",
                 engine='gpt-3.5-turbo',
                 max_query_len=1000, 
                 max_ans_token=2048, 
                 ) -> None:
        self._prompt = prompt
        self._engine = engine
        self._max_query_len = max_query_len
        self._max_ans_token = max_ans_token
    
    def _get_response(self, content):
        message_list = [
            {'role': 'user', 'content': f'{self._prompt}\n 文章：{content}'},
        ]

        response = openai.ChatCompletion.create(
            model=self._engine,
            messages = message_list,
            max_tokens= self._max_ans_token,
            temperature=0,
            top_p=1,
            n=1,
            # # stop=stop if stop else None,
            presence_penalty=0,
            frequency_penalty=0,
        )
        output_keyword = response['choices'][0]['message']['content']
        output_keyword = output_keyword.split('\n')
        output_keyword = filter(lambda x:len(x)>2 and x[0]=='-', output_keyword)
        output_keyword = map(lambda x:x[1:].strip(), output_keyword)
        return list(output_keyword)

    def _clip_content(self, content):
        sentences = []
        cur_sentence = ''
        for d in content:
            cur_sentence += d
            if d in '。？！.?!':
                sentences.append(cur_sentence)
                cur_sentence = ''
        if cur_sentence:
            sentences.append(cur_sentence)
        cur_content = ''
        for sen in sentences:
            if len(cur_content+sen) > self._max_query_len:
                yield cur_content
                cur_content = sen
            else:
                cur_content += sen
        yield cur_content
    
    def get_new_keywords(self, contents):
        if RECORD_FILE_KEYWORD.exists():
            with open(RECORD_FILE_KEYWORD, 'r', encoding='utf-8')as f:
                record = json.load(f)
        else:
            record = {}
            
        new_keywords = []
        print('openai processing\n')
        for content in tqdm(contents):
            content = content.strip()
            if not content:
                continue
            
            for con in self._clip_content(content):
                if con[:100] in record:
                    cur_keywords = record[con[:100]]
                else:
                    try:
                        cur_keywords = self._get_response(con)
                        record[con[:100]] = cur_keywords
                    except:
                        print('-'*20)
                        print(con)
                        print('-'*20)
                        print(traceback.format_exc())
                        print('-'*20)
                        cur_keywords = []
                new_keywords.extend(cur_keywords)
        with open(RECORD_FILE_KEYWORD, 'w', encoding='utf-8')as f:
            json.dump(record, f, ensure_ascii=False, indent=4)
        return list(set(new_keywords))


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
            df_keyword = pd.read_excel(file_excel)
            df_keyword = df_keyword.loc[df_keyword.iloc[:, 1]=='是']
            df_keyword = df_keyword.iloc[:, 0]
            str_keyword = '\n'.join(df_keyword.tolist())
            with open(file_txt, 'w', encoding='utf-8')as f:
                f.write(str_keyword)
            print(f'keyword from {file_excel} to {file_txt}')
    
    @staticmethod
    def get_all_keywords():
        all_keywords = []
        for file in os.listdir(KEYWORD_FOLD):
            file = KEYWORD_FOLD/file
            if file.suffix != '.txt':
                continue
            all_keywords.extend(load_data_txt(file))
        return list(OrderedDict.fromkeys(all_keywords))
            
    
    @staticmethod
    def get_new_keywords():
        with open(RECORD_FILE_KEYWORD, 'r', encoding='utf-8')as f:
            queried_keywords = json.load(f)
        total_keywords = []
        for v in queried_keywords.values():
            total_keywords.extend(v)
        total_keywords = set(total_keywords)
        
        used_keywords = []
        for file in os.listdir(KEYWORD_FOLD):
            file = KEYWORD_FOLD/file
            if file.suffix not in ['.xls', '.xlsx']:
                continue
            df_keyword = pd.read_excel(file)
            used_keywords.extend(df_keyword.iloc[:, 0].tolist())
        used_keywords = set(used_keywords)
        
        new_keywords = total_keywords-used_keywords
        str_new_keywords = '\n'.join(new_keywords)
        
        with open('./dataspace/new_keywords.txt', 'w', encoding='utf-8')as f:
            f.write(str_new_keywords)


if __name__ == '__main__':
    sentence = '''看我的收藏0有用+1已投票0轨道器播报编辑锁定讨论上传视频特型编辑太空拖船轨道器是指往来于航天站与空间基地之间的载人或无人飞船。它的主要用途是更换、修理航天站上的仪器设备。补给消耗品，从航天站取回资料和空间加工的产品等。由于它专门来往于各个空间站，又被称为“太空拖船”。中文名轨道器别名太空拖船往返航天站与空间基地用途更换、修理航天站上的仪器设备相关视频查看全部轨道飞行器分为两种。一种是活动范围较小的，叫做轨道机动飞行器；另一种是在大范围内实行轨道转移的，成为轨道转移飞行器。可以搭载七名宇航员在太空至少逗留10天。机舱内有三层甲板：飞行甲板、中甲板和设有生命支持系统的底层甲板。轨道飞行器长37.24米，高17.27米，翼展29.79米，载荷舱尺寸18.3*4.6米，轨道速度每小时28800公里，可容忍温度1500摄氏度，轨道高度185公里至1000公里，持续时间10至16天。词条图册更多图册'''
    a = KeywordQueryer()
    print(a.get_new_keywords([sentence]))
    
    # KeywordManager.keyword_excel2txt()
    # print(KeywordManager.get_all_keywords())
    # KeywordManager.get_new_keywords()
    pass