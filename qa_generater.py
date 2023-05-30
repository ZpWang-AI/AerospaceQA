# -*- coding: utf-8 -*-

# In[1]
import openai
import time
import datetime
import logging
import multiprocessing
import pandas as pd

from openai_apikey import api_key

openai.api_key = api_key

def get_prompt(x):
    """给定数据x组装prompt并返回"""
    return x

def get_response(prompt):
    """给prompt调用api，并返回结果，模型及tempture等超参自定"""
    # PROMPT = """请根据给定文章生成航空航天领域相关知识的问题，并从文章中抽取问题的回答。\n
    #             输出格式：\n
    #             问题1；回答1 \n
    #             ...
    #             问题n；回答n \n
    #         """
    PROMPT = """
生成航空航天领域问题
请根据提供的航空航天领域相关文章，从文章中抽取部分文字(15个字内)，并为该文字生成对应的问题。抽取的文字为问题的答案。\n
示例输入：
文章：随着航空航天技术的不断发展，人们对于太空旅行和探索的热情不断高涨。SpaceX公司最近成功发射了一枚载人火箭，将四名宇航员送往国际空间站。这次任务的成功标志着航天技术又迈上了新的台阶。
示例输出：
Q: SpaceX最近发射的是什么类型的火箭？
A: 载人火箭。
Q: SpaceX的最新任务标志着什么？
A: 航天技术迈上了新的台阶。
"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.1,
        top_p=1,
        max_tokens=2048,    # 最大token个数根据model定
        messages=[
            { "role": "system", "content": f"{PROMPT}"},
            { "role": "user", "content": f"{prompt}" },
            { "role": "assistant", "content": "生成的问题和抽取的答案为："}
        ]
      )
    return completion

#In[1]
# debug_text = "这三种在设计、任务运作方式上都有很大差别。美国航天飞机的核心级发动机安装在轨道器上起到重复使用主发动机降低成本的作用，轨道器本身是航天运载器的核心组成部分，发射时出大力。苏俄的暴风雪航天飞机则基本是完全靠能源超重型运载火箭驮上天，轨道器上没主发动机只有最后用来执行远地点轨道插入的小轨道机动发动机，轨道器发射时不出力最后入轨时小推一把。算重复使用的大型载人货运多功能飞船。欧洲被取消的赫尔墨斯航天飞机完全是放在火箭顶端如同载人飞船一样发射到太空，最终版完全取消了载荷舱专心作为可重复使用的载人飞船角色。甚至对接口、太空行走气闸舱和轨道机动发动机放在可分离的尾部的资源舱里，是一次性的在重返大气层前抛掉。"
# completion = get_response(debug_text)

# In[1]
def get_result_from_response(res_context, input_text, paras, Ques, Ans, Ans_startIdx, Ans_EndIdx):
    """分析并处理调用api的返回结果，不同model不同参数，返回结构可能不一样，最好自己在notebook里看看"""
    res_context = res_context.choices[0].message.content

    all_data = res_context.split('\n\n')
    logging.warning("生成结果：{}".format(all_data))
    for idx in range(0, len(all_data)):
        # ques = all_data[idx].strip()
        # ans = all_data[idx + 1].strip()
        return_lst = all_data[idx].split('\n')
        if len(return_lst) <= 1:
            continue
        else:
            ques, ans = return_lst[0], return_lst[-1]
            ques, ans = ques[2:].strip(), ans[2:].strip()
            for i in range(8):
                # s.index('')
                start_idx = input_text.find(ans[i:8])
                # logging.warning(f'debug_start: {ans[i:8]}')
                if start_idx != -1:
                    break
            else:
                continue
            end_idx = start_idx + len(ans) - 1
            text_end_pos = len(input_text) - 1
            if end_idx > text_end_pos:
                end_idx = text_end_pos   
            paras.append(input_text)
            Ques.append(ques)
            Ans.append(ans)
            Ans_startIdx.append(start_idx)
            Ans_EndIdx.append(end_idx)
    
    logging.warning(f'result: {paras}, {Ques}, {Ans}, {Ans_startIdx}, {Ans_EndIdx}')
    return None

# In[1]
def sleep(id_thread):
    t = min(45, 5 + id_thread *3)
    logging.info(f"子进程{id_thread}开始睡眠了， 睡{t}秒")
    time.sleep(t)

def save_result(paras, Ques, Ans, Ans_startIdx, Ans_EndIdx, save_path):
    """保存结果，需要注意，每5次调用会保存一次，不要把之前的覆盖了"""
    # 从现有的 JSON 文件中读取数据
    # with open('./QA_data1.json', 'r') as f:
    #     existing_data = json.load(f)
    # existing_df = pd.DataFrame(existing_data)
    logging.warning('saving...............................')
    # existing_df = pd.read_json(save_path)

    # # 创建一个新的 DataFrame，其中包含要追加的数据
    # new_data = {'paragraph': paras, 'question': Ques, 'answer': Ans, 'start_idx': Ans_startIdx, 'end_idx': Ans_EndIdx}
    # new_df = pd.DataFrame(new_data)

    # # 将新数据追加到现有的 DataFrame
    # updated_df = existing_df.append(new_df, ignore_index=True)

    # # 将更新后的 DataFrame 保存为 JSON 文件
    # updated_df.to_json(save_path, orient='records', force_ascii=False)

    # 重新保存所有
    new_data = {'paragraph': paras, 'question': Ques, 'answer': Ans, 'start_idx': Ans_startIdx, 'end_idx': Ans_EndIdx}
    new_df = pd.DataFrame(new_data)
    new_df.to_json(save_path, orient='records', force_ascii=False)

# In[1]
def split_data(id_thread, i, x, paras, Ques, Ans, Ans_startIdx, Ans_EndIdx):
    breakTurn = 0
    response = None
    while True:                                           # 主要应对速度限制，这里除非报没钱了的错误，否则一直循环
        prompt = get_prompt(x)
        try:
            response = get_response(prompt)
            break
        except Exception as e:
            if isinstance(e, openai.error.RateLimitError) and \
                'You exceeded your current quota, please check your plan and billing details.' in e.user_message:
                logging.critical("你没钱了")                 # logger
                break
            else:                                           #不知名的错误
                logging.error(f"{id_thread} error message {e.user_message}")
                if breakTurn == 5:
                    break
                breakTurn += 1
                sleep(id_thread)

    if i % 3 == 0:          
        logging.warning(f"子进程{id_thread}正在第{i}次调用api 已获取结果")
    
    get_result_from_response(response, x,
                                paras, Ques, Ans, Ans_startIdx, Ans_EndIdx)

def thread_fun(id_thread, data, save_path):
    """
    每个进程所执行的程序，每个进程的处理数据过程写在此处
    x, y 进程函数参数
    """
    paras, Ques, Ans, Ans_startIdx, Ans_EndIdx = [],[],[],[],[]
    for i, x in enumerate(data):
        xlen = len(x)
        if xlen <= 600:
            logging.warning('input_text: ' + x)
            split_data(id_thread, i, x, paras, Ques, Ans, Ans_startIdx, Ans_EndIdx)
        else:
            x_mid = x[:600]
            x_right = x[600:1500]
            logging.warning('input_text: ' + x_mid)
            split_data(id_thread, i, x_mid, paras, Ques, Ans, Ans_startIdx, Ans_EndIdx)
            logging.warning('input_text: ' + x_right)
            split_data(id_thread, i, x_right, paras, Ques, Ans, Ans_startIdx, Ans_EndIdx)

        if i % 5 == 0:
            save_result(paras, Ques, Ans, Ans_startIdx, Ans_EndIdx, save_path)

    save_result(paras, Ques, Ans, Ans_startIdx, Ans_EndIdx, save_path)
    return None

# In[1]
import json

# baike
with open('./dataspace/baike.all_crawled_info.jsonl', 'r', encoding='utf-8') as f:
    baike_cont = []
    for line in f:
        json_data = json.loads(line.strip())

        # 分别提取content1和content2的内容
        if json_data['content'] != '':
            baike_cont.append(json_data['content'])
    
# print(baike_cont, len(baike_cont))

# zhidao
with open('./dataspace/zhidao.all_crawled_info.jsonl', 'r', encoding='utf-8') as f:
    zhidao_cont1, zhidao_cont2 = [], []
    for line in f:
        json_data = json.loads(line.strip())

        # 分别提取content1和content2的内容
        if json_data['content1'] != '':
            zhidao_cont1.append(json_data['content1'])
        if json_data['content2'] != '':
            zhidao_cont2.append(json_data['content2'])
    
# print(zhidao_cont1, len(zhidao_cont1))
# print(zhidao_cont2, len(zhidao_cont2))

# In[1]
# 调用api，生成问题和答案
if __name__=='__main__':
    DEBUG = True
    num_thread = 1 if not DEBUG else 1
    thread_src_ref_pre = [zhidao_cont1, zhidao_cont2, baike_cont]                      # 每个元素对应着thread要处理的那一批数据（按下标对应）
    save_path = './output/'                        # save_path

    pool = multiprocessing.Pool(processes=num_thread)
    processes = []
    for i in range(0, num_thread):
        p = pool.apply_async(thread_fun, (i, thread_src_ref_pre[i], save_path+'QA'+str(i)+'.json'))
        processes.append(p)
    pool.close()
    pool.join()
    for p in processes:
        p.get()
