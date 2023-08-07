from pathlib import Path as path

# baike
BAIKE_ALL_INFO_FILE_JSONL = path('./dataspace/baike.all_crawled_info.jsonl')
BAIKE_CRAWLED_FILE_JSONL = path('./dataspace/baike.crawled_keyword.jsonl')
BAIKE_NOT_FOUND_FILE_TXT = path('./dataspace/baike.not_found_keyword_list.txt')
BAIKE_LOG_FILE_TXT = path('./dataspace/baike.log.txt')
BAIKE_ERROR_FILE_TXT = path('./dataspace/baike.error.txt')

# zhidao
ZHIDAO_ALL_INFO_FILE_JSONL = path('./dataspace/zhidao.all_crawled_info.jsonl')
ZHIDAO_CRAWLED_KEYWORD_FILE_JSON = path('./dataspace/zhidao.crawled_keyword.json')
# ZHIDAO_CRAWLED_KEYWORD_FILE_JSONL = path('./dataspace/zhidao.crawled_keyword.jsonl')
ZHIDAO_LOG_FILE_TXT = path('./dataspace/zhidao.log.txt')
ZHIDAO_ERROR_FILE_TXT = path('./dataspace/zhidao.error.txt')

PROXY_URL = '''
https://api.xiaoxiangdaili.com/ip/get?appKey=981028115805786112&appSecret=VwrmCHtQ&cnt=&wt=text

'''.strip()
PROXY_URL = ''

# key extraction
DATA_FOLD = path('./dataspace/')
KEYWORD_FOLD = path('./dataspace/keywords/')
# KEYWORD_QUERY_FILE_JSON = path('./dataspace/keyword.query.json')
KEYWORD_QUERY_FILE_JSONL = path('./dataspace/keyword.query.jsonl')
# KEYWORD_FILTER_FILE_JSON = path('./dataspace/keyword.filter.json')
KEYWORD_FILTER_FILE_JSONL = path('./dataspace/keyword.filter.jsonl')

# openai api
OPENAI_ERROR_FILE_TXT = path('./dataspace/openai.error.txt')
OPENAI_TOKEN_FILE_JSONL = path('./dataspace/openai.tokens.jsonl')