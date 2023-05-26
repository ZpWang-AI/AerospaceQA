import requests
import time


proxy_url = 'https://api.xiaoxiangdaili.com/ip/get?appKey=979275302268456960&appSecret=21LsaFF5&cnt=&wt=text'


def get_proxy(return_str=False):
    for i in range(1, 4):
        response = requests.get(proxy_url)
        proxy = str(response.text)
        if 'false' not in proxy:
            if return_str:
                return proxy
            else:
                return {'http': proxy, 'https': proxy}
        print(f'{proxy_url} can\'t get proxy, retry {i}')
        time.sleep(5)
    return None