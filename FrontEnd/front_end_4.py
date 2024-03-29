import json
import requests
import cv2
import os
import gradio as gr
import pandas as pd

from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes
from typing import *

from utils import split_p2s

'''
多线程
异常处理

LOGO
修改字体颜色，深蓝色
对话框底边对齐
改为英文

'''

LOGO_FILEPATH = 'file/FrontEnd/2.png'  # 'file/' + 相对路径


class ServerAPI:
    @staticmethod
    def retrieve_passages(query:str) -> List[str]:
        """
        根据查询返回答案
        
        param:
            query
        return:
            list of passage
        """
        # return '相关文章'
        
        target_url = 'http://47.103.108.50:8002/search?query='
        url = target_url+query
        datas = requests.get(url).text
        try:
            datas = json.loads(datas)
            # datas: [[passage, url], ...]
        except:
            print('=== error datas ===')
            print(datas)
        return [p[0]for p in datas] if type(datas) == list else ['无相关信息']*5
        # return texts if texts else '无相关信息'

    @staticmethod
    def ner_query(query:str) -> List[str]:
        """
        NER命名实体检测
        
        param:
            query
        return:
            entities: list of str
        """
        target_url = 'http://47.103.108.50:8004/ner?question=' + query
        datas = requests.post(target_url).text
        datas = eval(datas)
        return datas["entity_list"]
    
    @staticmethod
    def entity_linking(entities: List[str]) -> dict:
        """
        entity linking实体替换
        
        param:
            entities: list of str
        return:
            dict: {entity: linked entity}
        """
        return {'神五':'神舟五号', '神六':'神舟六号'}
    
    @staticmethod
    def mrc_extraction(query:str, passages:List[str]) -> Union[str, None]:
    # def mrc_extraction(query:str, passage:str) -> Union[str, None]:
        """
        通过MRC模型，根据相关文章，抽取对应查询的答案
        
        param:
            query: 查询
            passage: 相关文章
        return:
            answer(str)
        """
        # return passages[0][1:]
        # return None
        # jsondata = json.dumps({"question": query, "context": passage})
        if ("中国空间站" in query or "天宫号空间站" in query or "天宫空间站" in query) and len(query) <=9:
            data = requests.get("http://localhost:8056/tiangong").text
        elif "历史上的今天" == query or query == "历史上的今天发生了什么？":
            mrc_answer = json.loads(requests.get("http://localhost:8056/history").text)
            url, title = mrc_answer[0], mrc_answer[1]
            data = "事件：" + title + "\n了解详情： " + url
        else:
            #####
            passage = "".join(passages[:5])
            passage = split_p2s(passage)
            #####
            target_url = 'http://47.103.108.50:8088/mrc?question=' +query + '&context='+passage
            data = requests.post(target_url).text
            data = eval(data)
            data = data["output"]
        return data

    @staticmethod
    def QA_abstract(history: List[List[str]]) -> str:
        """
        历史对话摘要
        
        param:
            history: [[query, answer], ...]
        return:
            abstract: str
        """
        return '历史对话摘要'
    
    @staticmethod
    def answer_generate(query:str, mrc_answer:Union[str, None], abstract:str) -> str:
        """
        根据提问、MRC抽取出的答案、对话历史摘要，生成系统回答
        
        param:
            query: str
            mrc_answer: str
            abstract: str
        return:
            system_answer: str
        """
        if mrc_answer is None:
            mrc_answer = '无抽取答案'
        return '\n'.join([query, mrc_answer, abstract])


class FrontEndTheme(Base):
    def __init__(self):
        super().__init__(
            # primary_hue=colors.blue,
            # secondary_hue=colors.blue,
            neutral_hue=colors.blue,
        )
        super().set(
            button_primary_background_fill_hover='*neutral_50',
            button_secondary_background_fill_hover='*neutral_50',
            button_cancel_background_fill_hover='*neutral_50',
        )


def main_front_end():
    with gr.Blocks() as demo:
        # gr.Markdown('''<div align='center' ><font size='70'>航空航天问答系统</font></div>''')
        logo_width = 400
        logo_md = f'''
        <div  align="center">
        <img src="{LOGO_FILEPATH}" width = "{logo_width}" height = "{logo_width//5}" alt="图片名称" align=center />
        </div>
        '''
        gr.Markdown(value=logo_md)
        
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(label='Chatting Thread', height=595)
                msg = gr.Textbox(placeholder='Press ENTER for chatting', label='Question \ Requirement')
                with gr.Row():
                    undo_button = gr.Button(value='Withdraw')
                    clear_button = gr.Button(value=' Clear ')
                    
            with gr.Column():
                with gr.Accordion('PreProcessing (NER and Entity Linking)', open=True):
                    ner = gr.Dataframe(headers=['Named Entity'], type='pandas')
                with gr.Accordion('Retriever', open=True):
                    retrieve_components = []
                    for p in range(1, 6):
                        with gr.Tab(f'Top-{p} PF'):
                            con = gr.HTML(show_label=False)
                            con = gr.Textbox(show_label=False, container=False, lines=10, max_lines=10)
                            retrieve_components.append(con)
                with gr.Accordion('Extractive MRC', open=True):
                    mrc_textbox = gr.HighlightedText(
                        # value=[' ', None],
                        label='',
                        combine_adjacent=True,
                        # container=False,
                        # show_legend=True,
                        # show_label=False,
                        color_map={'Answer': 'green', 'Answer is not in the passages': 'yellow'},
                        scale=5,
                        # visible=False,
                    )
                    mrc_textbox.value = [('\n', None)]
                with gr.Accordion('对话历史摘要', open=True, visible=False):
                    qa_abstract = gr.Textbox(show_label=False, value=' ', container=False)
    
            def undo_func(chat_history):
                if chat_history:
                    chat_history.pop()
                return chat_history
            undo_button.click(fn=undo_func, inputs=chatbot, outputs=chatbot)

            def clear_func():
                return (
                    '',
                    [],
                    pd.DataFrame({'Named Entity':[]}),
                    *([' ']*5),
                    [('\n', None)],
                    ' ',
                )
            clear_button.click(
                fn=clear_func,
                outputs=[
                    msg,
                    chatbot, 
                    ner,
                    *retrieve_components,
                    mrc_textbox,
                    qa_abstract,
                ]
            )

            def respond(message, chat_history):
                query = message
                entities = ServerAPI.ner_query(query)
                linking_entities = ServerAPI.entity_linking(entities)
                passages = ServerAPI.retrieve_passages(query)
                mrc_answer = ServerAPI.mrc_extraction(query, passages)
                abstract = ServerAPI.QA_abstract(chat_history)
                # system_answer = ServerAPI.answer_generate(query, mrc_answer, abstract)
                system_answer = mrc_answer

                def format_mrc_answer():
                    if mrc_answer is None:
                        return []
                    for p, passage in enumerate(passages):
                        if mrc_answer in passage:
                            p_start = passage.index(mrc_answer)
                            p_end = p_start+len(mrc_answer)
                            return [
                                (passage[:p_start], None), 
                                (passage[p_start:p_end], 'Answer'),
                                (passage[p_end:], None),
                            ]
                    return [(mrc_answer, 'Answer is not in the passages')]
                
                chat_history.append([message, system_answer])
                
                entities = pd.DataFrame({'Named Entity':entities})
                passages = (passages+['无相关信息']*5)[:5]
            
                return (
                    '',
                    chat_history,
                    entities,
                    *passages,
                    format_mrc_answer(),
                    abstract
                )
            msg.submit(
                fn=respond, 
                inputs=[msg, chatbot], 
                outputs=[
                    msg,
                    chatbot, 
                    ner,
                    *retrieve_components,
                    mrc_textbox,
                    qa_abstract,
                ]
            )
            
    demo.launch(
        share=False,
        debug=False,
    )

    
if __name__ == '__main__':
    main_front_end()