import gradio as gr
import json
import pandas as pd
import requests
from typing import *


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
        
        target_url = 'http://106.15.232.22:8778/search?query='
        url = target_url+query
        datas = requests.get(url).text
        try:
            datas = json.loads(datas)
            # datas: [[passage, url], ...]
        except:
            print('=== error datas ===')
            print(datas)
        return [p[0]for p in datas] if type(datas) == list else ['无相关信息']*5

    @staticmethod
    def ner_query(query:str) -> List[str]:
        """
        NER命名实体检测
        
        param:
            query
        return:
            entities: list of str
        """
        return ['神五', '神六']
    
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
        """
        通过MRC模型，根据相关文章，抽取对应查询的答案
        
        param:
            query: 查询
            passage: 相关文章
        return:
            answer(str)
        """
        return passages[0][1:]
        # return None
        # jsondata = json.dumps({"question": query, "context": passage})
        target_url = 'http://127.0.0.1:8081/mrc?question=' +query + '&context='+passage
        # target_url = 'http://127.0.0.1:8081/mrc'
        # url = target_url+query+'@@&&@@'+passage
        data = requests.post(target_url).text
        # data = requests.post(target_url, data=json.dumps({"question": query, "context": passage}, ensure_ascii=False)).text
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


def main_front_end():
    with gr.Blocks() as demo:
        gr.Markdown('''航空航天问答系统
                    ''')
        
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(label='聊天框').style(height=600)
                msg = gr.Textbox(placeholder='输入回车以发出信息', label='输入框')
                with gr.Row():
                    undo_button = gr.Button(value='撤销')
                    clear_button = gr.Button(value='清除')
                    
            with gr.Column():
                # ner&linking, retrieve, mrc
                with gr.Accordion('命名实体识别', open=True):
                    ner = gr.outputs.Dataframe(headers=['实体'], type='pandas')
                with gr.Accordion('检索', open=True):
                    retrieve_components = []
                    for p in range(1, 6):
                        with gr.Tab(f'相关信息{p}'):
                            con = gr.Text(show_label=False, container=False)
                        retrieve_components.append(con)
                with gr.Accordion('抽取式机器阅读理解', open=True):
                    mrc_textbox = gr.HighlightedText(
                        # value=[' ', None],
                        # label='',
                        combine_adjacent=True,
                        container=False,
                        # show_legend=True,
                        # show_label=False,
                    )
                    mrc_textbox.style(color_map={
                        '抽取出的答案': 'green',
                    })
                with gr.Accordion('对话历史摘要', open=True):
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
                    pd.DataFrame({'实体':[]}),
                    *([' ']*5),
                    ' ',
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
                system_answer = ServerAPI.answer_generate(query, mrc_answer, abstract)

                def format_mrc_answer():
                    if mrc_answer is None:
                        return []
                    formatted = []
                    for p, passage in enumerate(passages):
                        if mrc_answer in passage:
                            # formatted.append([f'相关信息{p+1}', 'y'])
                            # formatted.append(['\n', None])
                            p_start = passage.index(mrc_answer)
                            p_end = p_start+len(mrc_answer)
                            formatted.extend(map(list, zip(passage, [None]*len(passage))))
                            for q in range(p_start, p_end):
                                formatted[q][1] = '抽取出的答案'
                            return formatted
                    print('No answer')
                    return []
                        
                chat_history.append([message, system_answer])
                
                entities = pd.DataFrame({'实体':entities})
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
            
    demo.launch(share=True)

    
if __name__ == '__main__':
    main_front_end()