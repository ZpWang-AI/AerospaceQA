import os
import json
import pandas as pd

from pathlib import Path as path

from data_utils import load_data
from keyword_extraction import KeywordManager
from settings import (BAIKE_ALL_INFO_FILE,
                      BAIKE_NOT_FOUND_FILE,
                      BAIKE_ERROR_FILE,
                      ZHIDAO_ALL_INFO_FILE,
                      ZHIDAO_CRAWLED_KEYWORD_FILE,
                      ZHIDAO_CRAWLED_URL_FILE,
                      ZHIDAO_ERROR_FILE,
                      RECORD_FILE_KEYWORD,
                      RECORD_FILE_FILTER,
                      KEYWORD_FOLD,
                      OPENAI_ERROR_FILE,
                      )


def count_file_line(file_path):
    line_cnt = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for _ in file:
            line_cnt += 1
    return line_cnt


class Analyzer:
    @staticmethod
    def analyze_crawled_result():
        baike_found:int
        baike_not_found:int
        baike_todo:int
        
        zhidao_keyword_found:int
        zhidao_keyword_todo:int
        # zhidao_keyword_cnt:int
        zhidao_url_found:int
        zhidao_url_todo:int
        
        keyword_query_done:int
        keyword_query_todo:int
        keyword_query_cnt:int
        keyword_filter_yes:int
        keyword_filter_no:int
        keyword_filter_todo:int
        keyword_manual_yes:int
        keyword_manual_no:int
        keyword_manual_todo:int
        
        baike_found = count_file_line(BAIKE_ALL_INFO_FILE)
        baike_not_found = count_file_line(BAIKE_NOT_FOUND_FILE)
        
        zhidao_keyword_found = 0
        zhidao_keyword_cnt = 0
        for keyword, urls in load_data(ZHIDAO_CRAWLED_KEYWORD_FILE, default={}).items():
            zhidao_keyword_found += 1
            zhidao_keyword_cnt += len(urls)
        zhidao_url_found = count_file_line(ZHIDAO_ALL_INFO_FILE)
        zhidao_url_todo = zhidao_keyword_cnt-zhidao_url_found
        
        keyword_query_done = 0
        keyword_query_cnt = set()
        for k, v in load_data(RECORD_FILE_KEYWORD, default={}).items():
            keyword_query_done += 1
            keyword_query_cnt.update(v)
        keyword_query_cnt = len(keyword_query_cnt)
        keyword_query_todo = baike_found+zhidao_url_found-keyword_query_done
        
        filter_res = load_data(RECORD_FILE_FILTER, default={})
        keyword_filter_yes = list(filter_res.values()).count(True)
        keyword_filter_no = len(filter_res)-keyword_filter_yes
        keyword_filter_todo = keyword_query_cnt-len(filter_res)
        
        keyword_manual_yes = len(KeywordManager.get_total_keywords())
        keyword_manual_total = set()
        for file in os.listdir(KEYWORD_FOLD):
            cur_file = KEYWORD_FOLD/file
            if cur_file.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(cur_file)
                df = df.iloc[:, 0]
                keyword_manual_total.update(df.tolist())
        keyword_manual_total = len(keyword_manual_total)
        keyword_manual_no = keyword_manual_total-keyword_manual_yes
        keyword_manual_todo = keyword_filter_yes-keyword_manual_total
        
        baike_todo = set(KeywordManager.get_total_keywords()) - \
                     set([p['keyword']for p in load_data(BAIKE_ALL_INFO_FILE)]) - \
                     set(load_data(BAIKE_NOT_FOUND_FILE))
        baike_todo = len(baike_todo)
        zhidao_keyword_todo = keyword_manual_yes-zhidao_keyword_found
        
        final_res = {
            '百度知道':{
                '根据关键词爬取文章':{
                    '已爬取':baike_found,
                    '不存在':baike_not_found,
                    '待爬取':baike_todo,
                },
            },
            '百度百科':{
                '根据关键词搜索网址':{
                    '已搜索':zhidao_keyword_found,
                    '待搜索':zhidao_keyword_todo,
                },
                '根据网址爬取文章':{
                    '已爬取':zhidao_url_found,
                    '待爬取':zhidao_url_todo,
                },
            },
            '关键词':{
                '根据文章提取关键词':{
                    '已提取':keyword_query_done,
                    '待提取':keyword_query_todo,
                    '关键词数量':keyword_query_cnt,
                },
                ' ChatGPT筛选关键词':{
                    '筛选为是':keyword_filter_yes,
                    '筛选为否':keyword_filter_no,
                    '待筛选':keyword_filter_todo,
                },
                '人工筛选关键词':{
                    '筛选为是':keyword_manual_yes,
                    '筛选为否':keyword_manual_no,
                    '待筛选':keyword_manual_todo,
                },
            },
        }
        
        # print(json.dumps(final_res, indent=4, ensure_ascii=False))

        def print_line(*args):
            print(*args, sep='\n', end='\n')
            
        for domain, domain_res in final_res.items():
            print_line(domain)
            for task, task_res in domain_res.items():
                print_line('    '+task)
                for key, val in task_res.items():
                    normalized_val = f'{val//1000},{str(val%1000).rjust(3, "0")}' if val >= 1000 else str(val)
                    normalized_val = normalized_val.rjust(11)
                    print_line('        '+key+'　'*(5-len(key))+normalized_val)
            
    
    @staticmethod
    def analyze_error():
        # error_file = BAIKE_ERROR_FILE
        # error_file = ZHIDAO_ERROR_FILE
        error_file = OPENAI_ERROR_FILE
        error_content = load_data(error_file)
        prefix = '>> error '
        error_lines = []
        for line in error_content:
            if line[:len(prefix)] == prefix:
                error_lines.append(line)
        for line in error_lines:
            if 'Max retries exceeded with url' not in line and \
                'Bad gateway' not in line:
            # if 1:
                print(line)
        pass
    

if __name__ == '__main__':
    Analyzer.analyze_crawled_result()
    # Analyzer.analyze_error()