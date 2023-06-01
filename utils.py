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
        # ====================
        break
        # ====================
    except BaseException as err:
        if retry_cnt == 1:
            es = '\n'.join(map(str, [
                '=='*10,
                message,
                '-'*10,
            ]))
            print(es)
        es = '\n'.join(map(str, [
            traceback.format_exc(),
            f'>> retry {retry_cnt} <<',
            f'>> error {str(err)} <<',
            '-'*10, 
        ]))
        print(es)
        if retry_cnt == retry_time:
            break
        else:
            sleep_random_time(3)
            
'''