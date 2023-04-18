import os
import sys

from pathlib import Path as path
# from selenium import webdriver
from selenium.webdriver.common.by import By
from msedge.selenium_tools import EdgeOptions, Edge

sys.setrecursionlimit(10**8)


EDGE_LOCATION = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
EDGEDRIVER_LOCATION = r"D:\msedgedriver.exe"
SAVED_FOLD = r"./saved"

start_urls = [
    r''
]


class Crawler:
    def __init__(self, edge_loc, edgedriver_loc, saved_fold) -> None:
        options = EdgeOptions()
        options.use_chromium = True
        options.binary_location = edge_loc
        self.driver = Edge(options=options, executable_path=edgedriver_loc)
        self.driver.get('www.baidu.com')  # For test
        
        self.saved_fold = path(saved_fold)
        self.saved_fold.mkdir(parents=True, exist_ok=True)
        
        self.searched_urls = set()
        
    def search_webpage(self, webpage):
        if webpage in self.searched_urls:
            return
        self.searched_urls.add(webpage)

        self.driver.get(webpage)
        elements = self.driver.find_elements(By.XPATH, '//meta')

        nxt_urls = self.deal_elements(elements)
        for url in nxt_urls:
            self.search_webpage(url)
    
    def deal_elements(self, elements):
        # TODO
        pass

    
def main():
    crawler = Crawler(
        edge_loc=EDGE_LOCATION,
        edgedriver_loc=EDGEDRIVER_LOCATION,
        saved_fold=SAVED_FOLD,
    )
    
    for url in start_urls:
        crawler.search_webpage(url)
    

if __name__ == '__main__':
    main()