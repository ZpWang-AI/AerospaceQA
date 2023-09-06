import os
import json
import pandas as pd
import datetime

from pathlib import Path as path

from data_utils import load_data, dump_data
from settings import (BAIKE_ALL_INFO_FILE_JSONL,
                      BAIKE_CRAWLED_FILE_JSONL,
                      BAIKE_NOT_FOUND_FILE_TXT,
                      ZHIDAO_ALL_INFO_FILE_JSONL,
                      ZHIDAO_CRAWLED_KEYWORD_FILE_JSON,
                      KEYWORD_FOLD,
                      KEYWORD_QUERY_FILE_JSONL,
                      KEYWORD_FILTER_FILE_JSONL,
                      
                      BAIKE_ERROR_FILE_TXT,
                      ZHIDAO_ERROR_FILE_TXT,
                      OPENAI_ERROR_FILE_TXT,
                      )


def _decorator_sort_deduplicate(func):
    def new_func(return_set=False):
        ret = func()
        ret = set(map(str, ret))
        return ret if return_set else sorted(ret)
    return new_func


def _decorator_custom(func):
    return _decorator_sort_deduplicate(staticmethod(func))


class KeywordProcesser:
    @staticmethod
    def _clean_func(keyword):
        keyword = str(keyword)
        keyword = keyword.strip()
        for sym in '()（）,.，。':
            keyword = keyword.strip(sym)
        keyword = keyword.strip()
        return keyword
    
    @staticmethod
    def _filter_func(keyword):
        try:
            float(keyword)
            return False
        except:
            pass
        
        if sum(keyword.count(sym) for sym in ',，') >= 3:
            return False
        
        return True

    @staticmethod
    def process_func(keywords):
        keywords = map(KeywordProcesser._clean_func, keywords)
        keywords = filter(KeywordProcesser._filter_func, keywords)
        return set(keywords)


# class DataManager:
#     baike_info_jsonl = 'baike.info.jsonl'
#     baike_found_jsonl = 'baike.found.jsonl'
#     baike_not_found_jsonl = 'baike.not_found.jsonl'
    
#     zhidao_info_jsonl = 'zhidao.info.jsonl'
#     zhidao_found_jsonl = 'zhidao.found.jsonl'
#     zhidao_not_found_jsonl = 'zhidao.not_found.jsonl'
    
#     def __init__(self, proxy_pool_url='') -> None:
#         now = datetime.datetime.now()
#         self._data_fold = path(f'./dataspace/data_{now.year}-{now.month}-{now.day}')
        
#         self._baike_info_jsonl = self._data_fold/
#         self._ = self._data_fold/
#         self._ = self._data_fold/
#         self._baike_log_txt = path('./dataspace/baike.log.txt')
#         self._baike_error_txt = path('./dataspace/baike.error.txt')
        
#         self._ = self._data_fold/
#         self._ = self._data_fold/
#         self._ = self._data_fold/
#         self._zhidao_log_txt = path('./dataspace/zhidao.log.txt')
#         self._zhidao_error_txt = path('./dataspace/zhidao.error.txt')
        
#         # https://api.xiaoxiangdaili.com/ip/get?appKey=981028115805786112&appSecret=VwrmCHtQ&cnt=&wt=text
#         self._proxy_pool_url = proxy_pool_url.strip()
        
#         self._keyword_fold = path('./dataspace/keywords/')
#         self._keyword_query_jsonl = self._data_fold/'keyword.query.jsonl'
#         self._keyword_filter_jsonl = self._data_fold/'keyword.filter.jsonl'
        
#         self._openai_error_txt = path('./dataspace/openai.error.txt')
#         self._openai_token_jsonl = path('./dataspace/openai.tokens.jsonl')
        
#     def baike_
        

class DataManager:
    '''
baike
    k_found
    u_found
    k_not_found
    k_todo = final-k_found-k_not_found
zhidao
    k_found
    k_todo = final-k_found
    u_found (1&2)
keyword
    query
        u_done
        u_todo = baike_u_found+zhidao_u_found-u_done
        k_found
    filter
        k_done
        k_yes
        k_no
        k_todo = query_k_found-k_done
    manual
        k_done
        k_yes = final
        k_no = k_done-k_yes
        k_todo = filter_yes-k_done
    '''
    
    @_decorator_custom
    def keyword_final():
        keyword_final = []
        for file in os.listdir(KEYWORD_FOLD):
            file = KEYWORD_FOLD/file
            if file.suffix == '.txt':
                keyword_final.extend(load_data(file))
        return keyword_final
    
    # ============================ baike
    @_decorator_custom
    def baike_k_found():
        return map(lambda x:x['keyword'], load_data(BAIKE_CRAWLED_FILE_JSONL, []))
    
    @_decorator_custom
    def baike_u_found():
        return map(lambda x:x['url'], load_data(BAIKE_CRAWLED_FILE_JSONL, []))
        
    @_decorator_custom
    def baike_k_not_found():
        return load_data(BAIKE_NOT_FOUND_FILE_TXT, [])
    
    @_decorator_custom
    def baike_k_todo():
        k_total = DataManager.keyword_final(return_set=True)
        k_found = DataManager.baike_k_found(True)
        k_not_found = DataManager.baike_k_not_found(True)
        return k_total-k_found-k_not_found
        
    # ============================ zhidao
    @_decorator_custom
    def zhidao_k_found():
        crawled_record = load_data(ZHIDAO_CRAWLED_KEYWORD_FILE_JSON, {})
        return filter(
            lambda k: any(v is True for v in crawled_record[k].values()),
            crawled_record,
        )
        
    @_decorator_custom
    def zhidao_k_todo():
        return DataManager.keyword_final(True) - \
               DataManager.zhidao_k_found(True)
    
    @_decorator_custom
    def zhidao_u_found():
        crawled_record = load_data(ZHIDAO_CRAWLED_KEYWORD_FILE_JSON, {})
        u_found = []
        for k in crawled_record:
            u_found.extend(filter(
                lambda u: crawled_record[k][u] is True,
                crawled_record[k],
            ))
        u_found_ = []
        for u in u_found:
            u_found_.extend([u+'@@1', u+'@@2'])
        return u_found_
     
     
    # ============================ keyword query
    @_decorator_custom
    def keyword_query_u_done():
        return load_data(KEYWORD_QUERY_FILE_JSONL, {}, merge_jsonl=True).keys()
    
    @_decorator_custom
    def keyword_query_u_todo():
        baike_u_found = DataManager.baike_u_found(True)
        zhidao_u_found = DataManager.zhidao_u_found(True)
        query_u_done = DataManager.keyword_query_u_done(True)
        return (baike_u_found | zhidao_u_found) - query_u_done
               
    @_decorator_custom
    def keyword_query_k_found():
        k_values = load_data(KEYWORD_QUERY_FILE_JSONL, {}, merge_jsonl=True).values()
        k_found = []
        for v in k_values:
            k_found.extend(v)
        return k_found
     
    # ============================ keyword filter
    @_decorator_custom
    def keyword_filter_k_done():
        return load_data(KEYWORD_FILTER_FILE_JSONL, {}, merge_jsonl=True).keys()

    @_decorator_custom
    def keyword_filter_k_yes():
        filter_record = load_data(KEYWORD_FILTER_FILE_JSONL, {}, merge_jsonl=True)
        return filter(lambda k:filter_record[k], filter_record)
    
    @_decorator_custom
    def keyword_filter_k_no():
        filter_record = load_data(KEYWORD_FILTER_FILE_JSONL, {}, merge_jsonl=True)
        return filter(lambda k:not filter_record[k], filter_record)
        
    @_decorator_custom
    def keyword_filter_k_todo():
        return DataManager.keyword_query_k_found(True) - \
               DataManager.keyword_filter_k_done(True)
               
    # ============================ keyword manual
    @_decorator_custom
    def keyword_manual_k_done():
        k_done = []
        for file in os.listdir(KEYWORD_FOLD):
            file = KEYWORD_FOLD/file
            if file.suffix in ['.xls', '.xlsx']:
                for sheet_name in pd.ExcelFile(file).sheet_names:
                    df_keyword = pd.read_excel(file, header=None, sheet_name=sheet_name)
                    df_keyword = df_keyword.iloc[:, 0].tolist()
                    k_done.extend(df_keyword)
        return k_done
               
    @_decorator_custom
    def keyword_manual_k_yes():
        return DataManager.keyword_final()  
               
    @_decorator_custom
    def keyword_manual_k_no():
        return DataManager.keyword_manual_k_done(True) - \
               DataManager.keyword_manual_k_yes(True)
               
    @_decorator_custom
    def keyword_manual_k_todo():
        filter_k_yes = KeywordProcesser.process_func(DataManager.keyword_filter_k_yes(True))
        manual_k_done = KeywordProcesser.process_func(DataManager.keyword_manual_k_done(True))
        return filter_k_yes-manual_k_done
    
    # ============================ key point
    def keypoint_total_message(*args, **kwargs):
        baike_u_found = DataManager.baike_u_found(*args, **kwargs)
        zhidao_u_found = DataManager.zhidao_u_found(*args, **kwargs)
        return baike_u_found | zhidao_u_found
    
    def keypoint_total_queried_keywords(*args, **kwargs):
        filter_yes = DataManager.keyword_filter_k_yes(*args, **kwargs)
        filter_no = DataManager.keyword_filter_k_no(*args, **kwargs)
        return filter_yes | filter_no

    def keypoint_total_manual_keywords(*args, **kwargs):
        return DataManager.keyword_manual_k_done(*args, **kwargs)
        
    # ============================ 
    @staticmethod
    def deduplicate_info(info_file):
        contents = load_data(info_file, ())
        init_len = len(contents)
        new_contents = []
        urls = set()
        for p in contents:
            if not p:
                continue
            if p['url'] not in urls:
                urls.add(p['url'])
                new_contents.append(p)
        os.remove(info_file)
        print(f'deduplicate {info_file}, init {init_len}, rest {len(urls)}')
        for p in new_contents:
            dump_data(info_file, p, mode='a')
        print('done')
        
    @staticmethod
    def clean_empty_baike_info():
        pass
            
    # ============================
    @staticmethod
    def analyse_progress():
        analyse_res = {
            '百度百科':{
                '根据关键词爬取文章':{
                    '已爬取':DataManager.baike_k_found,
                    '不存在':DataManager.baike_k_not_found,
                    '待爬取':DataManager.baike_k_todo,
                },
            },
            '百度知道':{
                '根据关键词搜索网址、爬取文章':{
                    '已爬取':DataManager.zhidao_k_found,
                    '待爬取':DataManager.zhidao_k_todo,
                    '文章数量':DataManager.zhidao_u_found,
                },
            },
            '关键词':{
                '根据文章提取关键词':{
                    '已提取':DataManager.keyword_query_u_done,
                    '待提取':DataManager.keyword_query_u_todo,
                    '关键词数量':DataManager.keyword_query_k_found,
                },
                ' ChatGPT筛选关键词':{
                    '筛选为是':DataManager.keyword_filter_k_yes,
                    '筛选为否':DataManager.keyword_filter_k_no,
                    '待筛选':DataManager.keyword_filter_k_todo,
                },
                '人工筛选关键词':{
                    '筛选为是':DataManager.keyword_manual_k_yes,
                    '筛选为否':DataManager.keyword_manual_k_no,
                    '待筛选':DataManager.keyword_manual_k_todo,
                },
            },
            '重点':{
                '重点':{
                    '爬取文章总量':DataManager.keypoint_total_message,
                    '抽取术语总量':DataManager.keypoint_total_queried_keywords,
                    '人工审核关键词数量':DataManager.keypoint_total_manual_keywords,
                }
            }
        }
        
        def print_line(*args):
            print(*args, sep='\n', end='\n')
            
        for domain, domain_res in analyse_res.items():
            print_line(domain)
            for task, task_res in domain_res.items():
                print_line('    '+task)
                for key, val in task_res.items():
                    val = len(val(True))
                    normalized_val = f'{val//1000},{str(val%1000).rjust(3, "0")}' if val >= 1000 else str(val)
                    normalized_val = normalized_val.rjust(11)
                    print_line('        '+key+'　'*(5-len(key))+normalized_val)
        
    @staticmethod
    def analyze_error():
        # error_file = BAIKE_ERROR_FILE_TXT
        # error_file = ZHIDAO_ERROR_FILE_TXT
        error_file = OPENAI_ERROR_FILE_TXT
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
    # sample = DataManager.zhidao_u_found()
    # sample = DataManager.keyword_query_k_found()
    # sample = DataManager.keyword_filter_k_yes()
    # print(sample)
    # print(len(sample))
    # DataManager.keyword_manual_k_todo()
    
    # DataManager.deduplicate_info(BAIKE_ALL_INFO_FILE_JSONL)
    # DataManager.deduplicate_info(ZHIDAO_ALL_INFO_FILE_JSONL)

    DataManager.analyse_progress()
    
    # with open('total_keywords.txt', 'w', encoding='utf-8')as f:
    #     keywords = DataManager.keypoint_total_manual_keywords(return_set=False)
    #     for k in keywords:
    #         f.write(f'{k}\n')
        
    
    # queried = DataManager.keyword_query_k_found(True)
    # filtered = DataManager.keyword_filter_k_done(True)
    # print(len(queried-filtered))
    # print(len(filtered-queried))
    # print(filtered-queried)