# AerospaceQA

The knowledge base of QA about aerospace.

### Step 1: Web crawling

Plan of the first step in acquiring knowledge by web crawlers: [【腾讯文档】航空航天问答项目——爬取计划](https://docs.qq.com/doc/DT3VubFhDenl5cVJj)

[【Python爬虫 • selenium】selenium4新版本使用指南 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/572134119)

[g1879/DrissionPage: 基于python的网页自动化工具。既能控制浏览器，也能收发数据包。可兼顾浏览器自动化的便利性和requests的高效率。功能强大，内置无数人性化设计和便捷功能。语法简洁而优雅，代码量少。 (github.com)](https://github.com/g1879/DrissionPage)

##### File structure

```
|	demo.py
|	crawler.py
|	postprocesser.py
|	saved_res
	|	0
		|	url.txt
		|	page_source.txt
		|	url_links.txt
		|	yes.txt  # a mark file meaning the url has been visited
	|	1
		...  # same files as fold "0"
	...
```
