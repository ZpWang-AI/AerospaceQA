import re
import requests
import random
import time
import json
import sys
import os
import traceback

from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import sleep_random_time
from proxy_utils import get_proxy
from data_utils import load_data, dump_data
from settings import (BAIKE_ALL_INFO_FILE,
                      BAIKE_CRAWLED_FILE,
                      BAIKE_NOT_FOUND_FILE,
                      BAIKE_LOG_FILE,
                      BAIKE_ERROR_FILE,)


url_prefix = " https://baike.baidu.com/item/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def log_info(*args, sep=' '):
    info = sep.join(args)
    print(info)
    dump_data(BAIKE_LOG_FILE, info, mode='a')
    

class BaikeSpider():
    def __init__(self, retry_time=3, proxy_url=None, sleep_time=2.5, only_abstrct=False) -> None:
        self._crawled = [line['keyword']for line in load_data(BAIKE_CRAWLED_FILE)]
        self._not_found = load_data(BAIKE_NOT_FOUND_FILE)
        self._crawled = set(self._crawled)
        self._not_found = set(self._not_found)
        
        self._retry_time = retry_time
        self._proxy_url = proxy_url
        self._sleep_time = sleep_time
        self._only_abstract = only_abstrct

    def _deal_piece(self, keyword, url, soup):
        title = soup.find('h1').get_text()
        if title in self._crawled or title in self._not_found:
            return
        main_content = soup.find('div', class_='main-content').get_text().replace('\n', ' ').replace('\xa0', ' ')
        main_content = re.sub(r'收藏查看我的收藏\d*有用\+\d*已投票\d*', '', main_content)
        main_content = re.sub(r'\[\d*\]', '', main_content)
        
        links = []
        filter_list = ['秒懂本尊答', '秒懂大师说', '秒懂看瓦特', '秒懂五千年', '秒懂全视界', '百科热词团队']
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'item' in href:
                for filter_word in filter_list:
                    if filter_word in href:
                        break
                else:
                    links.append("https://baike.baidu.com" + href)

        data_piece = {
            "keyword": keyword, 
            "url": url,
            "title": title,
            "content": main_content,
            "linked_links:": links,
        }
        return data_piece
    
    def _crawl_one_piece(self, keyword):
        if keyword in self._crawled or keyword in self._not_found:
            log_info(keyword + " has benn crawled already.")
            return
        
        url = url_prefix+keyword
        response = requests.get(
            url=url, 
            headers=headers, 
            proxies=get_proxy(proxy_url=self._proxy_url, return_str=False),
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('div', class_='main-content')
        if content is None:
            self._not_found.add(keyword)
            dump_data(BAIKE_NOT_FOUND_FILE, keyword, mode='a')
            log_info(keyword + " not found in Baidu Baike")
        else:
            self._crawled.add(keyword)
            data_piece = self._deal_piece(keyword, url, soup)
            dump_data(BAIKE_ALL_INFO_FILE, data_piece, mode='a')
            crawled_piece = {'keyword': keyword, 'url': url}
            dump_data(BAIKE_CRAWLED_FILE, crawled_piece, mode='a')
            log_info(keyword + " found in Baidu Baike, now crawling...")

        sleep_random_time(self._sleep_time)
    
    def crawl_keywords(self, keyword_list):
        for keyword in keyword_list:
            try:
                self._crawl_one_piece(keyword=keyword)
            except BaseException as err:
                print('-'*10)
                print(keyword)             
                print('-'*10)
                print(err)
                print('-'*10)
                print(traceback.format_exc())
                print('-'*10)
                
   
# def LOG_info(message):
#     print(message)
#     with open(log_file, 'a+', encoding='utf-8') as writer:
#         writer.write(message + '\n')

# # get crawled keyword
# def get_already_crwal_set(crawled_keyword_file):
#     LOG_info('******************************************************************************')
#     LOG_info('loading crawled baike keyword...')
#     Crawled_keyword_set = set()
#     Crawled_url_set = set()
#     if not os.path.exists(crawled_keyword_file):
#         f = open(crawled_keyword_file, 'w', encoding='utf-8')
#         f.close()

#     with open(crawled_keyword_file, 'r', encoding='utf-8') as reader:
#         lines = reader.readlines()
#         for line in tqdm(lines, desc='crawling'):
#             a_data = json.loads(line)
#             Crawled_keyword_set.add(a_data["keyword"])
#             Crawled_url_set.add(a_data["url"])

#     LOG_info("done, " + str(len(Crawled_keyword_set)) + " keyword has been crawled from Baidu Baike")
#     return Crawled_keyword_set, Crawled_url_set

# # get not found keyword
# def get_not_found_set(not_found_word_file):

#     LOG_info('loading not found keyword set...')

#     if not os.path.exists(not_found_word_file):
#         f = open(not_found_word_file, 'w', encoding='utf-8')
#         f.close()

#     with open(not_found_word_file, 'r', encoding='utf-8') as reader:
#         lines = reader.readlines()

#     Not_found_set = set(map(lambda x: x.strip(), lines)) 
#     LOG_info('done, ' + str(len(Not_found_set)) + " keyword not found in Baidu Baike")
#     return Not_found_set


# given keyword, get url
# def get_crawl_url(keyword_list):

#     new_url_list = []
    
#     for keyword in keyword_list:
#         new_url_list.append([keyword, url_prefix + keyword])
    
#     return new_url_list


# given url, crawl content
# def crawl_content(url_list, Crawled_keyword_set, Crawled_url_set, Not_found_set):
#     total_data = []
#     for keyword, url in tqdm(url_list):
#         if keyword in Crawled_keyword_set or url in Crawled_url_set or keyword in Not_found_set:
#             LOG_info(keyword + " has benn crawled already.")
#             continue
#         # print(url+"")
#         # print(headers)
#         response = requests.get(url+"", headers=headers, proxies=get_proxy(return_str=False))
#         soup = BeautifulSoup(response.text, 'html.parser')
#         content = soup.find('div', class_='main-content')
#         # if keyword doest exist
#         if content == None :
#             LOG_info(keyword + " not found in Baidu Baike")
#             Not_found(keyword, Not_found_set)
#         else:
#             LOG_info(keyword + " found in Baidu Baike, now crawling...")
#             total_data.append(found_and_record(keyword, url, soup, Crawled_keyword_set, Crawled_url_set))

#         rest_time = random.random() * 5
#         LOG_info('rest for ' + str(rest_time) + "secs")
#         time.sleep(rest_time)
#     LOG_info('crawl done')
#     LOG_info('******************************************************************************')
#     return total_data

# def Not_found(key_word, Not_found_set):
#     if key_word in Not_found_set:
#         return
#     else:
#         with open(not_found_word_file, 'a+', encoding='utf-8') as writer:
#             writer.write(key_word + '\n')
#         Not_found_set.add(key_word)



# def record_keyword_allinfo(all_info_file, a_data, Crawled_keyword_set, Crawled_url_set):

#     with open(all_info_file, 'a+', encoding='utf-8') as writer:
#         json_str = json.dumps(a_data, ensure_ascii=False)
#         writer.write(json_str + '\n')
#     Crawled_keyword_set.add(a_data["keyword"])
#     Crawled_url_set.add(a_data["url"])



# def found_and_record(keyword, url, soup, Crawled_keyword_set, Crawled_url_set):
#     title = soup.find('h1').get_text()
#     if title in Crawled_keyword_set:
#         return
#     main_content = soup.find('div', class_='main-content').get_text().replace(' ', '').replace('\n', '').replace('\xa0', '')
#     main_content = re.sub(r'收藏查看我的收藏\d*有用\+\d*已投票\d*', '', main_content)
#     main_content = re.sub(r'\[\d*\]', '', main_content)
    
#     links = []
#     filter_list = ['秒懂本尊答', '秒懂大师说', '秒懂看瓦特', '秒懂五千年', '秒懂全视界', '百科热词团队']
#     for link in soup.find_all('a'):
#         href = link.get('href')
#         if href and 'item' in href:
#             for filter_word in filter_list:
#                 if filter_word in href:
#                     break
#             else:
#                 links.append("https://baike.baidu.com" + href)

#     a_data = {"keyword": keyword, 
#               "url": url,
#               "title": title,
#               "content": main_content,
#               "linked_links:": links}
    
#     record_keyword_allinfo(all_info_file, a_data, Crawled_keyword_set, Crawled_url_set)

#     with open(crawled_file, 'a+', encoding='utf-8') as writer:
#         crawled_data = json.dumps({'keyword': keyword, 'url': url}, ensure_ascii=False)
#         writer.write(crawled_data + '\n')
    
#     return a_data


# def crawl_main(keyword_list, Crawled_keyword_set, Crawled_url_set, Not_found_set):
#     new_url_list = get_crawl_url(keyword_list)

#     return crawl_content(new_url_list, Crawled_keyword_set, Crawled_url_set, Not_found_set)

    
# def read_keyword_file(keyword_file):
#     with open(keyword_file, 'r', encoding='utf-8') as reader:
#         lines = reader.readlines()
#         keyword = list(map(lambda x: x.strip(), lines))
#     return keyword


class Baike_spider():
    def __init__(self) -> None:
        Crawled_keyword_set, Crawled_url_set = get_already_crwal_set(crawled_file)
        self._crawled_keyword_set = Crawled_keyword_set
        self._crawled_url_set = Crawled_url_set
        self._not_found_set = get_not_found_set(not_found_word_file)
    
    def crawl_from_file(self, keyword_file):
        if not os.path.exists(keyword_file):
            print("file not exists, plz check again")    
            sys.exit(1)
        else:
            print('reading keyword file ....')

        keyword_list = read_keyword_file(keyword_file)

        origin_keyword_nums = len(self._crawled_keyword_set)
        origin_not_found_keywords_nums = len(self._not_found_set)

        total_nums = len(keyword_list)
        LOG_info('--------------------------------------')
        LOG_info("file_name:" + keyword_file + " contains " + str(total_nums) + " keyword in total will be crawled")
        LOG_info('Crawling...')
        LOG_info('....................')

        total_data = crawl_main(keyword_list, self._crawled_keyword_set, self._crawled_url_set, self._not_found_set)

        new_keywords = len(self._crawled_keyword_set) - origin_keyword_nums
        LOG_info(str(new_keywords) + " new keywords has been crawled")

        new_not_found_keywords = len(self._not_found_set) - origin_not_found_keywords_nums
        LOG_info(str(new_not_found_keywords) + " new keywords not found in Baidu Baike")
        return total_data

    def crawl_from_list(self, keyword_list):
        origin_keyword_nums = len(self._crawled_keyword_set)
        origin_not_found_keywords_nums = len(self._not_found_set)

        total_nums = len(keyword_list)
        LOG_info('--------------------------------------')
        LOG_info("keyword_list:" + " contains " + str(total_nums) + " keyword in total will be crawled")
        LOG_info('Crawling...')
        LOG_info('....................')

        total_data = crawl_main(keyword_list, self._crawled_keyword_set, self._crawled_url_set, self._not_found_set)

        new_keywords = len(self._crawled_keyword_set) - origin_keyword_nums
        LOG_info(str(new_keywords) + " new keywords has been crawled")

        new_not_found_keywords = len(self._not_found_set) - origin_not_found_keywords_nums
        LOG_info(str(new_not_found_keywords) + " new keywords not found in Baidu Baike")
        return total_data, self._not_found_set, self._crawled_keyword_set


# if __name__ == "__main__":
#     file_name1 = 'keyword_file/4_27_12_01.txt'
#     file_name2 = 'keyword_file/5_17_12_14.txt'
#     keyword_list = ['空间站', '卫星']
#     baike_spider = Baike_spider()
#     # 爬文件，一行一个关键词
#     baike_spider.crawl_from_file(file_name1)
#     # 爬list
#     baike_spider.crawl_from_list(keyword_list)

#     baike_spider.crawl_from_file(file_name2)

    # count = 0
    # not_found_count = 0
    # # 加载已经爬过的keyword
    # Crawled_keyword_set, Crawled_url_set = get_already_crwal_set(crawled_file)
    # # 加载不存在的keyword
    # Not_found_set = get_not_found_set(not_found_word_file)

    # # 需要爬取的keyword_file
    # # keyword_file = './keyword_file/4_27_12_01.txt'
    # keyword_file = sys.argv[1]

    # if not os.path.exists(keyword_file):
    #     print("file not exists, plz check again")    
    #     sys.exit(1)
    # else:
    #     print('reading keyword file ....')
    # keyword_list = read_keyword_file(keyword_file)

    # crawl_main(keyword_list)
    # res = str(count) + ' keyword has been collected. ' + \
    #         str(not_found_count) + " keyword not found. " + \
    #         str(len(keyword_list) - count - not_found_count) + "keyword repeated."
    # print(res)
    
    # # new_url_list = get_crawl_url(keyword_list)

    # # print(new_url_list)