import openai
import traceback
import time
import threading
import copy

from openai.error import RateLimitError

from openai_apikey import api_key
from data_utils import dump_data
from settings import (OPENAI_ERROR_FILE, 
                      OPENAI_TOKENS_FILE,
                      )

openai.api_key = api_key


def get_response_chatcompletion(
    messages=None,
    content=None,
    
    retry_time=3,
    wait_seconds=10,
    max_tokens=2048,
    engine='gpt-3.5-turbo',
    show_input=False,
    show_output=False,
    
    n=1,
    temperature=0.0,
    top_p=1.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    
):
    if messages is None and content is None:
        raise "no content"

    if messages is None:
        messages = [{ "role": "user", "content": content}]
        
    '''
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "Hello! It's nice to see you too. How can I assist you today?",
        "role": "assistant"
      }
    }
  ],
  "created": 1685415799,
  "id": "chatcmpl-7LjvjU2fIbRBFSgext3s8pOiu5hwv",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 17,
    "prompt_tokens": 17,
    "total_tokens": 34
  }
}
    '''
    if show_input:
        print(messages)
    retry_cnt = 0
    while 1:
        retry_cnt += 1
        try:
            chatcompletion = openai.ChatCompletion.create(
                messages=messages,
                model=engine,
                max_tokens=max_tokens,
                n=n,
                temperature=temperature,
                top_p=top_p,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
            )
            response = chatcompletion['choices'][0]['message']['content']
            tokens = chatcompletion['usage']
            dump_data(OPENAI_TOKENS_FILE, tokens, mode='a')
            if show_output:
                print(response)
            return response
        except RateLimitError as err:
            time.sleep(wait_seconds)
        except BaseException as err:
            if retry_cnt == 1:
                es = '\n'.join(map(str, [
                    '=='*10,
                    messages,
                    '-'*10,
                ]))
                print(es)
                dump_data(OPENAI_ERROR_FILE, es, 'a')
            es = '\n'.join(map(str, [
                traceback.format_exc(),
                f'>> retry {retry_cnt} <<',
                f'>> error {str(err)} <<',
                '-'*10
            ]))
            print(es)
            dump_data(OPENAI_ERROR_FILE, es, 'a')
            if retry_cnt == retry_time:
                return ''
            else:
                time.sleep(wait_seconds)


def get_response_chatcompletion_multithread(
    message_list=None,
    content_list=None,
    
    max_thread_cnt=8,
    
    retry_time=3,
    wait_seconds=10,
    max_tokens=2048,
    engine='gpt-3.5-turbo',
    show_input=False,
    show_output=False,
    
    n=1,
    temperature=0.0,
    top_p=1.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,
):
    if message_list is None and content_list is None:
        raise "no content"

    if message_list is None:
        message_list = [
            [{ "role": "user", "content": content}]
            for content in content_list
        ]
        
    cnt = len(message_list)
    response_list = ['']*cnt
    running_thread = [0]
    
    def thread_func(pid):
        running_thread[0] += 1
        response = get_response_chatcompletion(
            messages=message_list[pid],
            retry_time=retry_time,
            wait_seconds=wait_seconds,
            max_tokens=max_tokens,
            engine=engine,
            show_input=show_input,
            show_output=show_output,
            n=n,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        response_list[pid] = response
        running_thread[0] -= 1
    
    for pid in range(cnt):
        t = threading.Thread(target=thread_func, args=(pid,))
        if running_thread[0] < max_thread_cnt:
            t.start()
    return response_list


if __name__ == '__main__':
    content = 'Hello, I\'m glad to see you.'
    messages = [
        { "role": "system", "content": 'you are my friend'},
        { "role": "user", "content": content},
        { "role": "assistant", "content": "I'm glad to see you, too."}
    ]
    # print(get_response_chatcompletion(content=content, max_tokens=2))
    # print(get_response_chatcompletion(messages=messages))
    response_list = get_response_chatcompletion_multithread(
        message_list=[copy.deepcopy(messages)for _ in range(100)],
        max_thread_cnt=3,
    )
    print(response_list)