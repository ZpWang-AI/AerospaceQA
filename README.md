# 航空航天QA系统 -- 数据爬取

基于LLM的使用航空航天领域知识的QA系统，数据爬取部分。[Github地址(不含数据)](https://github.com/ZpWang-AI/AerospaceQA)

最终输出：百度知道 / 百度百科上的相关文章 和 航空航天相关的关键词

[TOC]



### 爬取步骤

1. 输入关键词，爬取百度知道/百度百科，获得 相关文章 （以及 其余信息，如 日期、网址 等）
2. 通过 GPT，从文章提取，得到关键词
3. 通过 GPT，筛选关键词，得到 质量更高的关键词
4. 通过 人工核对，筛选关键词，得到 合格关键词，继续用于爬取 

### 数据 (dataspace)

#### 数据地址

网盘地址：LPAI 实验室百度网盘，全部文件 / 航空航天项目data

文件夹中包含数个压缩包，文件名后缀为更新日期

#### dataspace 结构

~~~
| dataspace
	| backup  # 部分文件备份
	| keywords
		| keyword1.xlsx  # 人工标注的excel文件
		| keyword1.txt  # 脚本处理的对应关键词
		| keyword2.xlsx
		| keyword2.txt
	
	| README.md
	
	| baike.all_crawled_info.jsonl  # 百度百科相关文章
	| baike.crawled_keyword.jsonl
	| baike.not_found_keyword_list.txt
	| baike.log.txt
	| baike.error.txt
	
	| zhidao.all_crawled_info.jsonl  # 百度知道相关文章
	| zhidao.crawled_keyword.jsonl
	| zhidao.crawled_url.txt
	| zhidao.log.txt
	| zhidao.error.txt
	
	| keyword.query.jsonl  # GPT 提取文章关键词
	| keyword.filter.jsonl  # GPT 筛选关键词
	| openai.tokens.jsonl
	| openai.error.txt
	
	| final_keywords.txt  # 人工筛选后最终关键词
	| passage2keywords.jsonl  # 文章与对应（人工筛选后）关键词
	| data_info.txt  # 数据信息
~~~

### 运行代码

~~~python
# 爬取知道、百科
python zhidao_spider.py
python baike_spider.py
# GPT 提取关键词
from keyword_extraction import main_query_new_keywords
main_query_new_keywords()
# GPT 筛选关键词
from keyword_extraction import main_filter_new_keywords
main_filter_new_keywords()
# 生成 需要人工核对的数据，生成在 ./dataspace 中
python keyword_extraction.py
# 查询数据
python data_manager.py
# 生成 final_keywords.txt 与 passage2keywords.jsonl
python script_final_keywords.txt
python passage2keywords.jsonl
~~~

* 新建文件 openai_apikey.py 并写入

~~~
api_key = '###############'
~~~

* 本地脚本（未上传）

~~~
_zhidao.cmd
_baike.cmd
_query.cmd
_filter.cmd
~~~

### 文件结构（已过期）

```
| settings.py

| utils.py
| data_utils.py
| proxy_utils.py
| openai_api.py
| Trie.py

| baike_spider.py
| zhidao_norm.py
| zhidao_spider.py
| keyword_extraction.py

| crawled_data_norm.py
| main.py
| analyze.py

```

### 相关文档

[【腾讯文档】航空航天问答项目——爬取计划](https://docs.qq.com/doc/DT3VubFhDenl5cVJj)

[【腾讯文档】航空航天问答项目——prompt设计](https://docs.qq.com/doc/DT2F0aXpyVkdaWUVI)
