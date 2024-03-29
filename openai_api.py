import openai
import traceback
import time
import threading
import copy
import requests

from openai.error import RateLimitError, APIError, APIConnectionError, Timeout, AuthenticationError

from openai_apikey import api_key
from utils import exception_handling
from data_utils import dump_data
from settings import (OPENAI_ERROR_FILE_TXT, 
                      OPENAI_TOKEN_FILE_JSONL,
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
    
    def chat_func():
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
        dump_data(OPENAI_TOKEN_FILE_JSONL, tokens, mode='a')
        if show_output:
            print(response)
        return response
    
    def exception_handle_func(err):
        if type(err) == RateLimitError:
            if 'please check your plan and billing details' in str(err):
                raise Exception('No more money !!!')
            return True
        if type(err) == APIConnectionError and 'Max retries exceeded with url' in str(err):
            return 5
        if type(err) == APIError and 'Bad gateway' in str(err):
            return True
        if type(err) == APIError and 'HTTP code 502' in str(err):
            return True
        if type(err) == Timeout and 'Max retries exceeded with url' in str(err):
            return True
        if type(err) == AuthenticationError:
            if 'this API key has been deactivated' in str(err):
                raise Exception('this API key has been deactivated')
            if 'Incorrect API key provided' in str(err):
                raise Exception('Incorrect API key provided')
            return True

    return exception_handling(
        target_func=chat_func,
        display_message=messages,
        error_file=OPENAI_ERROR_FILE_TXT,
        error_return='',
        exception_handle_func=exception_handle_func,
        retry_time=retry_time,
        sleep_time=wait_seconds,
    )

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
    thread_list = []
    
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
            thread_list.append(t)
            t.start()
    for t in thread_list:
        t.join()
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