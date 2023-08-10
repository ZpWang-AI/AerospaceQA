import hashlib

from pathlib import Path as path


### cookie & headers

COOKIE = 'BIDUPSID=5DCF64B6004B252A81F76175A4834F38; PSTM=1667449230; BDUSS=p2QkY1SEwxRGdGYXVBQThQY2dCb0VnT1hYT35IT211UDRQSGN0UVJtMFRiMU5rSVFBQUFBJCQAAAAAAAAAAAEAAADnX5k1bHBhaWVyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABPiK2QT4itkb2; BDUSS_BFESS=p2QkY1SEwxRGdGYXVBQThQY2dCb0VnT1hYT35IT211UDRQSGN0UVJtMFRiMU5rSVFBQUFBJCQAAAAAAAAAAAEAAADnX5k1bHBhaWVyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABPiK2QT4itkb2; ZFY=w:ATSNrQvPH5ztdAGHlkeR:AOfrvJHplaw6117QTb23Rc:C; BAIDUID=5DCF64B6004B252A99DB2293A90E562A:SL=0:NR=10:FG=1; BAIDUID_BFESS=5DCF64B6004B252A99DB2293A90E562A:SL=0:NR=10:FG=1; __bid_n=1843bfd33dba27ebb54207; BAIDU_WISE_UID=wapp_1686416940048_995; FPTOKEN=uSKDrYmtx+tYTN2vgUXfF3X4jFgHaXvTRcrSn2uSSW3ihsM8NXsdpzSkm5qaEmrvinoo6hh4qnEYvoS9+9XcLAIVRPnlYD2joaCBP45PYS83IB112+Ya1l5g3SzNufK5gtl9DuNmidegdvGPkKbWI3CXrrOZG+rZmeu6yoiRSlbQ4/srGUJUsFJTXWzA0bakx+uthRzgknZka8iNfwC4/rclcHlpnqgUB8t2yJTPXoH7t6z2YBYkMInGYAfjpXKzvjyu09+2WWVJNTKXNh1FBaRmuw3N89J3cGzr6AlOMbEDZDzaP4oTtCXuJ3DHZ9Ba+1BwA39DfLrBMYND3Qm72MMwPgxWSdRh2WOE8PQ8m7glKoPreIB3+X+MU9GNlXuOP/T4mBQIit/VaSSSi+rtAQ==|9F4j8U/vG7KBNF/IC8kU0bIOdC4H5tdVFJbFm+w4A7g=|10|1ffffb79b6b1a27e10c9706dbe7792f4; delPer=0; PSINO=7; H_PS_PSSID=36549_39109_39160_38920_39114_39120_38918_26350_22157_39101_39043; BA_HECTOR=8ha0208l8g010g848485ah0m1id29hc1o'
if COOKIE is not None:
    if "__yjs_duid" not in COOKIE:
        COOKIE += "; __yjs_duid=1_" + str(hashlib.md5().hexdigest()) + "; "
    else:
        _ = COOKIE.split("__yjs_duid=")
        __ = _[1].split(";", 1)[-1]
        ___ = hashlib.md5()
        COOKIE = _[0] + "__yjs_duid=1_" + str(___.hexdigest()) + "; " + __
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Referer": "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=2&ch=&tn=baiduhome_pg&bar=&wd=123&oq=123&rsv_pq=896f886f000184f4&rsv_t=fdd2CqgBgjaepxfhicpCfrqeWVSXu9DOQY5WyyWqQYmsKOC%2Fl286S248elzxl%2BJhOKe2&rqlang=cn",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Sec-Fetch-Mode": "navigate",
    "COOKIE": COOKIE,
    "Connection": "Keep-Alive",
}

### baike

BAIKE_ALL_INFO_FILE_JSONL = path('./dataspace/baike.all_crawled_info.jsonl')
BAIKE_CRAWLED_FILE_JSONL = path('./dataspace/baike.crawled_keyword.jsonl')
BAIKE_NOT_FOUND_FILE_TXT = path('./dataspace/baike.not_found_keyword_list.txt')
BAIKE_LOG_FILE_TXT = path('./dataspace/baike.log.txt')
BAIKE_ERROR_FILE_TXT = path('./dataspace/baike.error.txt')


### zhidao

ZHIDAO_ALL_INFO_FILE_JSONL = path('./dataspace/zhidao.all_crawled_info.jsonl')
ZHIDAO_CRAWLED_KEYWORD_FILE_JSON = path('./dataspace/zhidao.crawled_keyword.json')
# ZHIDAO_CRAWLED_KEYWORD_FILE_JSONL = path('./dataspace/zhidao.crawled_keyword.jsonl')
ZHIDAO_LOG_FILE_TXT = path('./dataspace/zhidao.log.txt')
ZHIDAO_ERROR_FILE_TXT = path('./dataspace/zhidao.error.txt')

PROXY_URL = '''
https://api.xiaoxiangdaili.com/ip/get?appKey=981028115805786112&appSecret=VwrmCHtQ&cnt=&wt=text

'''.strip()
PROXY_URL = ''


### key extraction

DATA_FOLD = path('./dataspace/')
KEYWORD_FOLD = path('./dataspace/keywords/')
# KEYWORD_QUERY_FILE_JSON = path('./dataspace/keyword.query.json')
KEYWORD_QUERY_FILE_JSONL = path('./dataspace/keyword.query.jsonl')
# KEYWORD_FILTER_FILE_JSON = path('./dataspace/keyword.filter.json')
KEYWORD_FILTER_FILE_JSONL = path('./dataspace/keyword.filter.jsonl')


### openai api

OPENAI_ERROR_FILE_TXT = path('./dataspace/openai.error.txt')
OPENAI_TOKEN_FILE_JSONL = path('./dataspace/openai.tokens.jsonl')