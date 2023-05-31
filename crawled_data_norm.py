# utf-8
import json
import re
import collections
import unicodedata


class DataNormalizer:
    def __init__(self) -> None:
        self.spaces = {
            '\x10', '\x7f', '\x9d', '\xad', '\\x0a', '\\xa0', '\\x0d'
            '\f', '\n', '\r', '\t', '\v', '&#160;', '&nbsp;',
            '\u200b', '\u200e', '\u202a', '\u202c', '\ufeff', '\uf0d8', '\u2061', '\u1680', '\u180e',
            '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008',
            '\u2009', '\u200a', '\u2028', '\u2029', '\u202f', '\u205f', '\u3000',
        }
        self.remove_lst = [
            "\xa0",
            "2113", 
            "5261", 
            "4102", 
            "1653",
            "步骤阅读", # 注意需要针对具体的 case，分析模型预测的答案和实际的答案的差别来进行相应字段的清洗
            r"\^[A-Z]", # '^G', '^H', '^E'去除
            "相关视频查看全部目录",
            "展开全部",
            "\\n+",
            r"\[\d+\]",
            r"<.*?>",
        ]
        self.replace_regx_map = collections.OrderedDict({
            '唿': '呼',
            # r'文章摘自：': '',
            r'<(\d+)>': '\g<1>',
            r'(\!|\"|\#|\$|\%|\&|\'|\(|\)|\*|\+|\,|\-|\.|\/|\:|\;|\<|\=|\>|\?|\@|\[|\\|\]|\^|\_|\`|\{|\||\}|\~)\1{1,}': '\g<1>',
            r'("""|＃|＄|％|＆|＇|（|）|＊|＋|，|－|／|：|；|＜|＝|＞|＠|［|＼|］|＾|＿|｀|｛|｜|｝|～|｟|｠|｢|｣|､|　|、|〃|〈|〉|《|》|'
            r'「|」|『|』|【|】|〔|〕|〖|〗|〘|〙|〚|〛|〜|〝|〞|〟||〾|〿|–|—|‘|’|‛|“|”|„|‟|…|‧|﹏|﹑|﹔|·|！|？|｡|。)\1{1,}': '\g<1>',
        })
    
    def normalize(self, text):
        text = unicodedata.normalize('NFKC', text)
        
        not_chinese_lst = re.findall(r"[A-Za-z0-9]+", text)
        for w in not_chinese_lst:
            if len(w) > 40:
                text = text.replace(w[:58], "")
            
        for space in self.spaces:
            text = text.replace(space, ' ')
        text = re.sub(r'\s+', ' ', text)
        
        for p in self.remove_lst:
            text = re.sub(p, '', text)
        for p, q in self.replace_regx_map.items():
            text = re.sub(p, q, text)
        
        # 去重
        reg = r'([^0-9IX]+)(\1){2,}'
        for _ in range(6):
            temp = text
            text = re.sub(reg, lambda m: m.group(1), text)
            if len(text) == len(temp):
                break

        return text.strip()
    

if __name__ == '__main__':
    a = DataNormalizer()
    with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8')as f:
        all_content = f.readlines()
    for content in all_content:
        content = json.loads(content)
        print(content['content'])
        print('='*20)
        print(a.normalize(content['content']))
        break