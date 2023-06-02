import os

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


def get_file_line_count(file_path):
    line_count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for _ in file:
            line_count += 1
    return line_count


class Analyzer:
    @staticmethod
    def analyze_crawled_result():
        baike_found_cnt = get_file_line_count(BAIKE_ALL_INFO_FILE)
        baike_not_found_cnt = get_file_line_count(BAIKE_NOT_FOUND_FILE)
        baike_crawled_cnt = baike_found_cnt+baike_not_found_cnt
        
        zhidao_info_cnt = get_file_line_count(ZHIDAO_ALL_INFO_FILE)
        zhidao_key_cnt = 0
        zhidao_url_cnt = 0
        for keyword, urls in load_data(ZHIDAO_CRAWLED_KEYWORD_FILE, default={}).items():
            zhidao_key_cnt += 1
            zhidao_url_cnt += len(urls)

        query_content_cnt = 0
        queried_cnt = set()
        for k, v in load_data(RECORD_FILE_KEYWORD, default={}).items():
            query_content_cnt += 1
            queried_cnt.update(v)
        queried_cnt = len(queried_cnt)
        filtered_res = load_data(RECORD_FILE_FILTER, default={})
        filtered_cnt = len(filtered_res)
        rest_cnt = list(filtered_res.values()).count(True)
        manual_cnt = 0
        for file in os.listdir(KEYWORD_FOLD):
            cur_file = KEYWORD_FOLD/file
            if cur_file.suffix == '.txt':
                manual_cnt += get_file_line_count(cur_file)
        keyword_cnt = len(KeywordManager.get_total_keywords())
        
        baike_progress = baike_crawled_cnt/keyword_cnt
        zhidao_key_progress = zhidao_key_cnt/keyword_cnt
        zhidao_url_progress = zhidao_info_cnt/zhidao_url_cnt
        keyword_query_progress = query_content_cnt/(baike_found_cnt+zhidao_info_cnt)
        keyword_filter_progress = filtered_cnt/queried_cnt
        manual_progress = manual_cnt/rest_cnt

        print(
            f'baike:',
            f'  found     {baike_found_cnt}',
            f'  not found {baike_not_found_cnt}',
            f'  crawled   {baike_crawled_cnt}',
            sep='\n',
        )
        print(
            f'zhidao:',
            f'  key cnt   {zhidao_key_cnt}',
            f'  url cnt   {zhidao_url_cnt}',
            f'  crawled   {zhidao_info_cnt}',
            sep='\n',
        )
        print(
            f'keyword:',
            f'  queried   {queried_cnt}',
            f'  filtered  {filtered_cnt}',
            f'  rest      {rest_cnt}',
            f'  manual    {manual_cnt}',
            f'  todo      {keyword_cnt}',
            sep='\n',
        )
        
        def uniform_progress(progress_name:str, progress_num):
            return '  '+progress_name.ljust(10, ' ')+'%.2f' % (progress_num*100)
        
        print(
            f'progress:',
            uniform_progress('baike', baike_progress),
            uniform_progress('zd key', zhidao_key_progress),
            uniform_progress('zd url', zhidao_url_progress),
            uniform_progress('kw query', keyword_query_progress),
            uniform_progress('kw filter', keyword_filter_progress),
            uniform_progress('manual', manual_progress),
            sep='\n'
        )
    
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
    # Analyzer.analyze_crawled_result()
    Analyzer.analyze_error()