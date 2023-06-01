from pathlib import Path as path

# baike
BAIKE_ALL_INFO_FILE = path('./dataspace/baike.all_crawled_info.jsonl')
BAIKE_CRAWLED_FILE = path('./dataspace/baike.crawled_keyword.jsonl')
BAIKE_NOT_FOUND_FILE = path('./dataspace/baike.not_found_keyword_list.txt')
BAIKE_LOG_FILE = path('./dataspace/baike.log.txt')
BAIKE_ERROR_FILE = path('./dataspace/baike.error.txt')

# zhidao
ZHIDAO_ALL_INFO_FILE = path('./dataspace/zhidao.all_crawled_info.jsonl')
ZHIDAO_CRAWLED_KEYWORD_FILE = path('./dataspace/zhidao.crawled_keyword.json')
ZHIDAO_CRAWLED_URL_FILE = path('./dataspace/zhidao.crawled_url.txt')
ZHIDAO_LOG_FILE = path('./dataspace/zhidao.log.txt')
ZHIDAO_ERROR_FILE = path('./dataspace/zhidao.error.txt')

PROXY_URL = '''



'''.strip()

# key extraction
DATA_FOLD = path('./dataspace/')
KEYWORD_FOLD = path('./dataspace/keywords/')
RECORD_FILE_KEYWORD = path('./dataspace/queried_keywords.json')
RECORD_FILE_FILTER = path('./dataspace/filtered_keywords.json')

# openai api
OPENAI_ERROR_FILE = path('./dataspace/openai.error.txt')
OPENAI_TOKENS_FILE = path('./dataspace/openai.tokens.jsonl')