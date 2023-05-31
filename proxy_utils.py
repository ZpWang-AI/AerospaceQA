import requests
import time


def get_proxy(proxy_url, return_str=False):
    if not proxy_url:
        return 
    for i in range(1, 4):
        response = requests.get(proxy_url)
        proxy = str(response.text)
        if 'false' not in proxy:
            if return_str:
                return proxy
            else:
                return {'http': proxy, 'https': proxy}
        print(f'{proxy_url} can\'t get proxy, retry {i}')
        time.sleep(10)
    return 


if __name__ == '__main__':
    proxy_url = '''

https://api.xiaoxiangdaili.com/ip/get?appKey=981028115805786112&appSecret=VwrmCHtQ&cnt=&wt=text

'''.strip()

    proxies = get_proxy(proxy_url, return_str=False)
    print(proxies)
    # print(get_proxy(return_str=True))
    
    response = requests.get('http://www.baidu.com', proxies=proxies)
    print(response)
    print(response.text)