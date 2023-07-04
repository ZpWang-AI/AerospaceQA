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
    datas = json.loads(datas)
    return datas[0][0] if datas else '无相关信息'
    
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
    target_url = ''  # TODO
    url = target_url+query+'@@&&@@'+passage
    data = requests.get(url).text
    return data


def main_demo_retrieve_mrc():
    max_passage = 10
    max_model = 5
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=2):
                input_query = gr.inputs.Textbox(lines=2, placeholder='请输入查询', label='查询')
                output_passage = gr.outputs.Textbox(label='相关文章')
                with gr.Accordion('回答'):
                    output_answer_list = [gr.outputs.Textbox(label='').update(visible=False) for _ in range(max_model)]
                    output_answer_list[0].update(visible=True)
                pass
            # input_query.submit(
                
            # )
            with gr.Column(scale=1):
                choice_mrc_model = gr.CheckboxGroup(choices=['model1', 'model2', 'model3'])
    # def func_gr(query):
    #     passage = retrieve_passage(query)
    #     answer = mrc_answer(None, query, passage)
    #     return passage, answer
    
    # demo = gr.Interface(
    #     fn=func_gr,
    #     inputs=gr.Text(lines=2, label='提问'),
    #     outputs=[gr.Text(label='相关文章'), gr.Text(label='模型回答')],
    #     examples=[],
    #     title='检索与问答模块 Demo',
    #     description='',
    # )
    demo.launch(share=True)
    pass


def main_demo_retrieve_mrc2():
    model_funcs = [lambda x,y:f'hello {x} and {y}']*3
    model_names = ['1', '2', '3']

    def func_gr(query, model_choice):
        if not model_choice:
            model_choice = '1'
        passage = retrieve_passage(query)
        model = model_funcs[int(model_choice)-1]
        answer = mrc_answer(model, query, passage)
        return passage, answer
    
    demo = gr.Interface(
        func_gr,
        inputs=[
            gr.Text(lines=2, placeholder='请输入查询', show_label=False),
            gr.Radio(choices=model_names, label='使用模型'),
            # gr.CheckboxGroup
        ],
        outputs=[
            gr.Text(label='相关信息'),
            gr.Text(label='回答'),
        ]
    )
    demo.launch(share=True)
    
    
if __name__ == '__main__':
    main_demo_retrieve_mrc2()