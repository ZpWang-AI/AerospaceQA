import gradio as gr
import json
import requests


def retrieve_passage(query:str) -> str:
    """
    根据查询返回答案
    
    param:
        query
    return:
        passage
    """
    # return '相关文章'
    
    # target_url = "http://106.15.232.22:8778/hangkong/"
    # url = target_url+query
    # datas = requests.get(url).text
    # datas = json.loads(datas)["data"]
    # return datas[0]['data']['content'] if datas else '无相关信息'
    
    target_url = 'http://106.15.232.22:8778/search?query='
    url = target_url+query
    datas = requests.get(url).text
    try:
        datas = json.loads(datas)
    except:
        print('=== error datas ===')
        print(datas)
    return datas[0][0] if datas else '无相关信息'


def ner_query(query:str) -> dict:
    """
    通过NER与entity linking替换实体
    
    param:
        query
    return:
        entity: dict
    """
    return {'神五': '神舟五号', '神六': '神舟六号'}
    
    
def mrc_answer(model_name, query:str, passage:str) -> str:
    """
    通过MRC模型，根据相关文章，生成对应查询的答案
    
    param:
        model
        query: 查询
        passage: 相关文章
    return:
        answer(str)
    """
    return query+passage
    # jsondata = json.dumps({"question": query, "context": passage})
    target_url = 'http://127.0.0.1:8081/mrc?question=' +query + '&context='+passage
    # target_url = 'http://127.0.0.1:8081/mrc'
    # url = target_url+query+'@@&&@@'+passage
    data = requests.post(target_url).text
    # data = requests.post(target_url, data=json.dumps({"question": query, "context": passage}, ensure_ascii=False)).text
    data = eval(data)
    data = data["output"]
    return data


def main_front_end():
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.ClearButton([msg, chatbot])

        def respond(message, chat_history):
            passage = retrieve_passage(message)
            entity = ner_query(message)
            answer = mrc_answer(None, message, passage)
            
            passage = '相关信息\n'+passage
            entity = '实体替换\n'+', '.join(map(lambda x: f'{x[0]}: {x[1]}', entity.items()))
            answer = '回答\n'+answer
            chat_history.extend([
                (message, passage),
                (None, entity),
                (None, answer),
            ])
            return "", chat_history

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
    
    demo.launch(share=True)

    
if __name__ == '__main__':
    main_front_end()