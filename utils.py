import datetime
import time
import os
import sys
import traceback
import threading 
import torch
import random

from typing import *
from pathlib import Path as path


def get_cur_time(time_zone_hours=8, return_str=True):
    time_zone = datetime.timezone(offset=datetime.timedelta(hours=time_zone_hours))
    cur_time = datetime.datetime.now(time_zone)
    return cur_time.strftime('%Y-%m-%d_%H:%M:%S') if return_str else cur_time


def sleep_random_time(sleep_time):
    time.sleep(random.random()*sleep_time*2)
    

'''

retry_cnt = 0
while 1:
    retry_cnt += 1
    try:
        pass
    except BaseException as err:
        if retry_cnt == 1:
            print('=='*10)
            # print(messages)
            print('-'*10)
        print(traceback.format_exc())
        print(f'>> retry {retry_cnt} <<')
        print(f'>> error {str(err)} <<')
        print('-'*10)
        if retry_cnt == retry_time:
            # return ''
            pass
        else:
            time.sleep(wait_seconds)
            
            
'''