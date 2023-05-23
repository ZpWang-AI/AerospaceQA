# utf-8
import re
import string
import collections
import unicodedata

class normalizer:
    def __init__(self) -> None:
        self.spaces = {'\x10', '\x7f', '\x9d', '\xad', '\\x0a', '\\xa0', '\\x0d'
                                                            '\f', '\n', '\r', '\t', '\v', '&#160;', '&nbsp;',
          '\u200b', '\u200e', '\u202a', '\u202c', '\ufeff', '\uf0d8', '\u2061', '\u1680', '\u180e',
          '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008',
          '\u2009', '\u200a', '\u2028', '\u2029', '\u202f', '\u205f', '\u3000'}
        self.noise_tokens = [ "2113", "5261", "4102", "1653"]
        self.error_word_map =  {'唿': '呼'}
        self.remove_regx_map = collections.OrderedDict({
        r'\s+': ' ',
        r'<(\d+)>': '\g<1>',
        r'\^[A-Z]': '',  # '^G', '^H', '^E'去除
        r'步骤阅读': '',  # 注意需要针对具体的 case，分析模型预测的答案和实际的答案的差别来进行相应字段的清洗
        r'(\!|\"|\#|\$|\%|\&|\'|\(|\)|\*|\+|\,|\-|\.|\/|\:|\;|\<|\=|\>|\?|\@|\[|\\|\]|\^|\_|\`|\{|\||\}|\~)\1{1,}': '\g<1>',
        r'("""|＃|＄|％|＆|＇|（|）|＊|＋|，|－|／|：|；|＜|＝|＞|＠|［|＼|］|＾|＿|｀|｛|｜|｝|～|｟|｠|｢|｣|､|　|、|〃|〈|〉|《|》|'
        r'「|」|『|』|【|】|〔|〕|〖|〗|〘|〙|〚|〛|〜|〝|〞|〟||〾|〿|–|—|‘|’|‛|“|”|„|‟|…|‧|﹏|﹑|﹔|·|！|？|｡|。)\1{1,}': '\g<1>',
    })
        
    def _remove_space(self, text):
        for space in self.spaces:
            text = text.replace(space, '')
        text = text.strip()
        text = re.sub('\s+', ' ', text)
        return text


    def _clean_error_word(self, text):
        """
        错别字清洗，如 '唿'吸道,打招'唿'
        """
        for error_word in self.error_word_map:
            if error_word in text:
                text = text.replace(error_word, self.error_word_map[error_word])
        return text


    def _remove_html_tag(self, text):
        cleanr = re.compile('<.*?>')
        text = re.sub(cleanr, '', text)
        return text

    def _remove_by_regex(self,text):
        text = text.strip()

        for rgx in self.remove_regx_map:
            text = re.sub(rgx, self.remove_regx_map[rgx], text)

        return text


    def _clean_duplacte_words(self,text):
        """
        去除很多重复的词和标点符号
        """
        reg = r'([^0-9IX]+)(\1){2,}'
        for i in range(6):
            temp = text
            text = re.sub(reg, lambda m: m.group(1), text)
            if len(text) == len(temp):
                break
        return text
    
    def zhidao_norm(self, answer):
        answer = answer.encode('iso-8859-1', errors='ignore').decode('gb2312', errors='ignore') 
        unicodedata.normalize('NFKC', answer)
        answer = re.sub("\n展开全部\n", "", answer)
        answer = re.sub("展开全部", "", answer)
        answer = re.sub("\\n+", "", answer)
        answer = re.sub("\u3000", "", answer)
        answer = re.sub(r'\[\d+\]', "", answer)
        not_chinese_lst = re.findall("[A-Za-z0-9]+", answer)
        for w in not_chinese_lst:
            if 40 <= len(w) <= 58:
                answer = answer.replace(w, "")
            if len(w) > 58:
                answer = answer.replace(w[:58], "")
        for noisy_token in self.noise_tokens:
            answer = re.sub(noisy_token, "", answer)

        for noisy_data in ["bai", "du", "zhi", "dao", "copy"]:
            tmp_lst = re.findall(noisy_data + ".", answer)
            for tmp in tmp_lst:
                if len(tmp) == len(noisy_data) or not tmp[-1] in string.ascii_letters:
                    answer = answer.replace(noisy_data, "")
        answer = answer.replace("\xa0", "")
        return answer
    
    def cleaner(self, text):
        text = self.zhidao_norm(text)
        text = self._remove_space(text)
        text = self._clean_error_word(text)
        text = self._remove_html_tag(text)
        text = self._remove_by_regex(text)
        text = self._clean_duplacte_words(text)
        return text