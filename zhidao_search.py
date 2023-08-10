# import gradio as gr
import random
import time
import requests
import hashlib
from bs4 import BeautifulSoup

from urllib.parse import quote


class ZhidaoSearcher:
    def __init__(self,
                 headers=None,
                 proxies=None,
                 decode_mode='utf-8',
                 ) -> None:
        self._headers = headers
        self._proxies = proxies
        self._decode_mode = decode_mode
        
    @staticmethod
    def _parse_zhidao(content: str) -> dict:
        """解析百度知道搜索的页面源代码.

        Args:
            content (str): 已经转换为UTF-8编码的百度知道搜索HTML源码

        Returns:
            dict: 解析后的结果
        """
        def _format(s):
            return (
                s.strip()
                .replace("\xa0", "")
                .replace("\u2002", "")
                .replace("\u3000", "")
                .strip()
            )
            
        content = content.replace("\u00a0", "")
        bs = BeautifulSoup(content, "html.parser")
        # 搜索结果总数
        try:
            total = int(
                bs.find("div", class_="wgt-picker")
                .find("span", class_="f-lighter")
                .text.split("共", 1)[-1]
                .split("条结果", 1)[0]
                .replace(",", "")
            )
        except AttributeError:
            # 没有搜索结果
            return {"results": [], "total": 0}
        # 所有搜索结果
        list_ = bs.find("div", class_="list").findAll("dl")
        results = []
        for item in list_:
            # 屏蔽企业回答
            if "ec-oad" in item["class"]:
                continue
            # print(item.prettify() + '\n\n\n\n\n\n\n')
            # 标题
            title = item.find("dt").text.strip("\n")
            # 链接
            try:
                url = item.find("dt").find("a")["href"]
            except KeyError:
                url = item.find("dt").find("a")["data-href"]
            if item.find("dd", class_="video-content") is not None:
                # 问题
                __ = item.find("dd", class_="summary")
                question = __.text.strip("问：") if __ is not None else None
                item = item.find("div", class_="right")
                tmp = item.findAll("div", class_="video-text")
                # # 简介
                # des = self._format(tmp[2].text)
                answer = None
                # 回答者
                answerer = tmp[0].text.strip("\n").strip("回答:\u2002")
                # 发布日期
                date = _format(tmp[1].text.strip("时间:"))
                # 回答总数
                count = None
                # 赞同数
                try:
                    agree = int(tmp[2].text.strip("获赞:\u2002").strip("次"))
                except ValueError:
                    agree = 0
                    answer = tmp[2].text.strip()
                type_ = "video"
            else:
                # 回答
                __ = item.find("dd", class_="answer")
                answer = __.text.strip("答：") if __ is not None else None
                # 问题
                __ = item.find("dd", class_="summary")
                question = __.text.strip("问：") if __ is not None else None
                tmp = item.find("dd", class_="explain").findAll("span", class_="mr-8")
                # 发布日期
                date = (
                    item.find("dd", class_="explain").find("span", class_="mr-7").text
                )
                # 回答总数
                try:
                    count = int(str(tmp[-1].text).strip("\n").strip("个回答"))
                except:
                    count = None
                # 回答者
                answerer = (
                    tmp[(-2 if len(tmp) >= 2 else -1)]
                    .text.strip("\n")
                    .strip("回答者:\xa0")
                )
                # 赞同数
                __ = item.find("dd", class_="explain").find("span", class_="ml-10")
                agree = int(__.text.strip()) if __ is not None else 0
                type_ = "normal"
            # 生成结果
            result = {
                "title": title,
                "question": question,
                "answer": answer,
                "date": date,
                "count": count,
                "url": url,
                "agree": agree,
                "answerer": answerer,
                # "type": type_
            }
            results.append(result)  # 加入结果
        # 获取分页
        # wrap = bs.find("div", class_="pager")
        # pages_ = wrap.findAll("a")[:-2]
        # if "下一页" in pages_[-1].text:
        #     pages = pages_[-2].text
        # else:
        #     pages = pages_[-1].text
        return {
            "results": results,
            # 取最大页码
            # "pages": int(pages),
            "total": total,
        }

    def search_zhidao(self, keyword: str, pn=1):
        """
        输入关键词和查找页面（第几页），输出搜索序列
        
        param:
            keyword:    target keyword used to search
            pn:         the page wanted to search
        return:
            list of results:
                [
                    {
                        'title':...,
                        'question':...,
                        'answer':...,
                        'date':...,
                        'count':...,
                        'url':...,
                        'agree':...,
                        'answerer':...,
                    }
                    ...
                ]
        """
        url = (
            "https://zhidao.baidu.com/search?lm=0&rn=10&fr=search&pn=%d&word=%s"
            % ((pn - 1) * 10, quote(keyword))
        )

        response = requests.get(url, headers=self._headers, proxies=self._proxies)
        response.encoding = self._decode_mode

        code = response.text

        # print('='*30)
        # print(code)
        # print('='*30)

        result = ZhidaoSearcher._parse_zhidao(code)

        # print('='*30)
        # print(result)
        # print('='*30)

        return result['results']


if __name__ == "__main__":
    from settings import HEADERS
    sampler = ZhidaoSearcher(headers=HEADERS)
    ans = sampler.search_zhidao('蔡徐坤')['results']
    print(ans)
    print(len(ans))
    ans = sampler.search_zhidao('蔡徐坤', pn=2)['results']
    print(len(ans))