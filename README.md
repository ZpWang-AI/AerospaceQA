# 航空航天QA系统

基于LLM的使用航空航天领域知识的QA系统。

### 相关文档

[【腾讯文档】航空航天问答项目——爬取计划](https://docs.qq.com/doc/DT3VubFhDenl5cVJj)

[【腾讯文档】航空航天问答项目——prompt设计](https://docs.qq.com/doc/DT2F0aXpyVkdaWUVI)

### 文件结构

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

| dataspace
	| keywords
		| keyword1.xlsx
		| keyword1.txt
		| keyword2.xlsx
		| keyword2.txt
	| baike.all_crawled_info.jsonl
	| baike.crawled_keyword.jsonl
	| baike.not_found_keyword_list.txt
	| baike.log.txt
	| baike.error.txt
	| zhidao.all_crawled_info.jsonl
	| zhidao.crawled_keyword.json
	| zhidao.crawled_url.txt
	| zhidao.log.txt
	| zhidao.error.txt
	| queried_keywords.json
	| filtered_keywords.json
	| openai.tokens.jsonl
	| openai.error.txt
	| new_filtered_keywords.txt

```

### 注意事项

新建文件 openai_apikey.py 并写入

```
api_key = '###############'
```
