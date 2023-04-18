import os
import sys
import time

from pathlib import Path as path
# from selenium import webdriver
from selenium.webdriver.common.by import By
from msedge.selenium_tools import EdgeOptions, Edge

sys.setrecursionlimit(10**8)


EDGE_LOCATION = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EDGEDRIVER_LOCATION = r"D:\msedgedriver.exe"
SAVED_FOLD = r"./saved"

start_urls = [
    r'https://baike.baidu.com/item/%E8%88%AA%E7%A9%BA%E8%88%AA%E5%A4%A9?fromModule=lemma_search-box',
    
]


class Crawler:
    def __init__(
        self, 
        edge_loc, 
        edgedriver_loc, 
        saved_fold, 
        search_page_per_second=5,
    ) -> None:
        options = EdgeOptions()
        options.use_chromium = True
        options.binary_location = edge_loc
        self.driver = Edge(options=options, executable_path=edgedriver_loc)
        self.driver.get('https://www.baidu.com/')  # For test
        print('\ndriver works!\n')
        
        self.saved_fold = path(saved_fold)
        self.saved_fold.mkdir(parents=True, exist_ok=True)
        
        self.searched_urls = set()
        
        self.search_gap = 1/search_page_per_second
        self.last_search_time = 0
    
    def search_urls(self, urls):
        print('\nstart searching\n')
        for url in urls:
            self._search_webpage(url)
        self.driver.quit()
        print('\nfinish searching\n')
        
    def _search_webpage(self, webpage):
        if webpage in self.searched_urls:
            return
        self.searched_urls.add(webpage)
        
        time.sleep(max(0, self.last_search_time+self.search_gap-time.time()))
        self.last_search_time = time.time()

        self.driver.get(webpage)
        elements = self.driver.find_elements(By.XPATH, '//div')

        for ele in elements:
            if ele.get_attribute('class') == 'param':
                print(ele.text)
    
    def _deal_elements(self, elements):
        # TODO
        # for element in elements:
        #     if element.name == ''
        pass

    
def main():
    crawler = Crawler(
        edge_loc=EDGE_LOCATION,
        edgedriver_loc=EDGEDRIVER_LOCATION,
        saved_fold=SAVED_FOLD,
        search_page_per_second=5
    )
    
    crawler.search_urls(start_urls)
    
    
if __name__ == '__main__':
    main()