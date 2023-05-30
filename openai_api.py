import openai
import traceback
import time

from openai_apikey import api_key

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
            if show_output:
                print(response)
            return response
        except BaseException as err:
            if retry_cnt == 1:
                print('=='*10)
                print(messages)
                print('-'*10)
            # print(f'\n{err}\n')
            print(traceback.format_exc())
            print(f'>> retry {retry_cnt} <<')
            print('-'*10)
            if retry_cnt == retry_time:
                return ''
            else:
                time.sleep(wait_seconds)


if __name__ == '__main__':
    content = 'Hello, I\'m glad to see you.'
    messages = [
        { "role": "system", "content": 'you are my friend'},
        { "role": "user", "content": content},
        { "role": "assistant", "content": "I'm glad to see you, too."}
    ]
    print(get_response_chatcompletion(content=content, max_tokens=2))
    print(get_response_chatcompletion(messages=messages))